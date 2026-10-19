import io
import zipfile
from urllib.request import urlopen

import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import ConfusionMatrixDisplay, accuracy_score, classification_report
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from risk_checks import detect_risk_signals

DATA_URL = "https://archive.ics.uci.edu/static/public/228/sms+spam+collection.zip"

st.set_page_config(page_title="PhishGuard AI", page_icon="🛡️", layout="wide")
st.title("🛡️ PhishGuard AI")
st.subheader("AI-powered suspicious SMS and message checker")
st.write("Paste a text message to estimate whether it resembles spam or a potentially deceptive message. This demo combines a text-classification model trained on the UCI SMS Spam Collection dataset with transparent checks for selected high-risk requests.")
st.warning("This is a screening aid, not a guarantee. It classifies SMS-like text, not website URLs, and cannot prove a message is safe or malicious. Never share passwords, OTPs, or private information.")

@st.cache_data(show_spinner="Loading and preparing the SMS dataset...")
def load_dataset():
    with urlopen(DATA_URL, timeout=30) as response:
        archive_bytes = response.read()
    with zipfile.ZipFile(io.BytesIO(archive_bytes)) as archive:
        candidates = [n for n in archive.namelist() if n.endswith("SMSSpamCollection")]
        if not candidates:
            raise ValueError("Dataset file was not found in the UCI archive.")
        raw = archive.read(candidates[0]).decode("utf-8", errors="replace")
    rows = []
    for line in raw.splitlines():
        parts = line.split("\t", 1)
        if len(parts) == 2 and parts[0] in {"ham", "spam"}:
            rows.append((parts[0], parts[1].strip()))
    df = pd.DataFrame(rows, columns=["label", "message"])
    df = df.drop_duplicates(subset="message").dropna()
    df = df[df.message.str.len() > 0]
    if len(df) < 100:
        raise ValueError("The downloaded dataset appears incomplete.")
    return df

@st.cache_resource(show_spinner="Training the text-classification model...")
def train_model():
    df = load_dataset()
    x_train, x_test, y_train, y_test = train_test_split(
        df["message"], df["label"], test_size=0.2, random_state=42, stratify=df["label"]
    )
    model = Pipeline([
        ("tfidf", TfidfVectorizer(lowercase=True, strip_accents="unicode", ngram_range=(1, 2), min_df=2, sublinear_tf=True)),
        ("classifier", LogisticRegression(max_iter=1000, class_weight="balanced", random_state=42)),
    ])
    model.fit(x_train, y_train)
    predictions = model.predict(x_test)
    accuracy = accuracy_score(y_test, predictions)
    report = classification_report(y_test, predictions, output_dict=True, zero_division=0)
    return model, df, accuracy, report, y_test, predictions


with st.sidebar:
    st.header("How it works")
    st.markdown("1. Load labelled SMS examples.\n2. Convert text into TF-IDF features.\n3. Train a Logistic Regression classifier.\n4. Predict a label and show model confidence.")
    st.caption("Dataset: UCI SMS Spam Collection. Model training is cached during the session.")

try:
    model, dataset, accuracy, report, y_test, predictions = train_model()
except Exception as exc:
    st.error("The dataset could not be loaded or the model could not be trained. Check the app logs and internet access, then retry.")
    st.exception(exc)
    st.stop()

m1, m2, m3 = st.columns(3)
m1.metric("Training dataset", f"{len(dataset):,} messages")
m2.metric("Legitimate examples", f"{(dataset.label == 'ham').sum():,}")
m3.metric("Spam examples", f"{(dataset.label == 'spam').sum():,}")

st.divider()
st.header("Analyze a message")
examples = {
    "Choose a sample...": "",
    "Legitimate-style example": "Hi, are we still meeting at the library at 4 pm?",
    "Suspicious prize example": "Congratulations! You have won a free prize. Call now to claim your reward!",
    "Suspicious account example": "URGENT: Your account will be suspended. Click this link now to verify your details.",
}
choice = st.selectbox("Try a sample message", list(examples.keys()))
default_text = examples[choice]
message = st.text_area("Message text", value=default_text, height=140, placeholder="Paste the SMS or message you want to check...")
if st.button("Analyze message", type="primary", use_container_width=True):
    cleaned = message.strip()
    if not cleaned:
        st.warning("Enter a message first.")
    else:
        predicted = model.predict([cleaned])[0]
        probabilities = model.predict_proba([cleaned])[0]
        classes = list(model.named_steps["classifier"].classes_)
        confidence = float(probabilities[classes.index(predicted)]) * 100
        risk_signals = detect_risk_signals(cleaned)
        if predicted == "spam" or risk_signals:
            st.error("⚠️ Risk assessment: CAUTION — suspicious patterns detected")
            st.write(f"Machine-learning prediction: **{'Spam-like' if predicted == 'spam' else 'Legitimate-like'}**")
            if risk_signals:
                st.write("Additional safety checks found these warning signs:")
                for signal in risk_signals:
                    st.markdown(f"- {signal}")
            st.write("Never share passwords, PINs, or OTPs. Verify payment or account requests using an official channel you find independently.")
        else:
            st.success("No specific high-risk pattern was detected")
            st.write("The model did not classify this text as spam, and the extra checks found none of their configured warning signs. This does not guarantee the message or any link is safe.")
        c1, c2, c3 = st.columns(3)
        c1.metric("ML prediction", "Spam-like" if predicted == "spam" else "Legitimate-like")
        c2.metric("Model confidence", f"{confidence:.1f}%")
        c3.metric("Extra warning signs", str(len(risk_signals)))
        st.caption("Confidence is the model's estimated class probability, not a calibrated guarantee of safety. The additional checks are transparent rules, not learned or continuously updated AI.")
        # Display influential terms from the fitted linear model for a lightweight explanation.
        vectorizer = model.named_steps["tfidf"]
        classifier = model.named_steps["classifier"]
        features = vectorizer.get_feature_names_out()
        vector = vectorizer.transform([cleaned])
        weights = classifier.coef_[0]
        contribution = vector.multiply(weights).toarray().ravel()
        active = contribution.nonzero()[0]
        if len(active):
            ranked = sorted(active, key=lambda i: abs(contribution[i]), reverse=True)[:8]
            explanation = pd.DataFrame({"Term": [features[i] for i in ranked], "Influence": ["Spam-like" if contribution[i] > 0 else "Legitimate-like" for i in ranked], "Relative score": [round(float(contribution[i]), 3) for i in ranked]})
            st.subheader("Text features that influenced this result")
            st.dataframe(explanation, hide_index=True, use_container_width=True)
        else:
            st.info("The model found no known vocabulary features in this message, so its prediction may be unreliable.")

with st.expander("Model evaluation"):
    st.write(f"Held-out test accuracy: **{accuracy:.1%}** (80/20 stratified train/test split, random_state=42).")
    report_df = pd.DataFrame(report).transpose().round(3)
    st.dataframe(report_df, use_container_width=True)
    fig, ax = plt.subplots()
    ConfusionMatrixDisplay.from_predictions(y_test, predictions, labels=["ham", "spam"], display_labels=["Legitimate", "Spam"], cmap="Blues", ax=ax, colorbar=False)
    ax.set_title("Held-out test confusion matrix")
    st.pyplot(fig)
    plt.close(fig)

st.divider()
st.markdown("**Safety reminder:** PhishGuard AI is an educational prototype. Verify suspicious messages through an official channel you find independently. Do not rely on a model prediction alone.")
st.markdown("Dataset: [UCI SMS Spam Collection](https://archive.ics.uci.edu/dataset/228/sms+spam+collection) · Source code: [GitHub repository](https://github.com/pratham655/PhishGuard-AI)")
