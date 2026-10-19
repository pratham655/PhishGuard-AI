# PhishGuard AI 🛡️

An educational AI/ML application that classifies SMS-like text as **spam-like** or **legitimate-like**. It uses TF-IDF text features and Logistic Regression trained on the UCI SMS Spam Collection dataset.

> **Important:** This is a screening aid, not a security guarantee. It classifies message text, not URLs or websites. A legitimate-like prediction does not mean a message is safe.

## Features

- Enter a message or try built-in examples.
- Predict spam-like vs legitimate-like class.
- Show estimated model confidence and influential text features.
- Show dataset label counts, held-out evaluation metrics, and a confusion matrix.
- Cache the dataset and trained model for the Streamlit session.

## Tech stack

- Python
- Streamlit
- Pandas and NumPy (via dependencies)
- scikit-learn: TF-IDF + Logistic Regression
- Matplotlib

## Run locally

1. Install Python 3.10–3.12.
2. Clone the repository and enter the folder:

   ```bash
   git clone https://github.com/pratham655/PhishGuard-AI.git
   cd PhishGuard-AI
   ```

3. Create and activate a virtual environment (optional but recommended):

   **Windows PowerShell**
   ```powershell
   py -3.12 -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

   **macOS/Linux**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

4. Install dependencies and start the app:

   ```bash
   pip install -r requirements.txt
   streamlit run app.py
   ```

The app downloads the public dataset from the UCI Machine Learning Repository on first use, so an internet connection is required. Streamlit caches the loaded dataset and trained model.

## How it works

1. Downloads the UCI SMS Spam Collection dataset.
2. Removes duplicate/empty messages and separates the message text from its `ham`/`spam` label.
3. Uses a stratified 80/20 train/test split.
4. Converts messages to TF-IDF unigram and bigram features.
5. Trains a Logistic Regression classifier with balanced class weights.
6. Evaluates on held-out examples and reports accuracy, precision/recall/F1, and a confusion matrix.
7. For a user message, returns a predicted class, estimated probability, and weighted terms that influenced the prediction.

## Dataset and citation

Almeida, T. A., Gómez Hidalgo, J. M., & Yamakami, A. (2011). *Contributions to the Study of SMS Spam Filtering: New Collection and Results*. UCI Machine Learning Repository: [SMS Spam Collection](https://archive.ics.uci.edu/dataset/228/sms+spam+collection).

## Deliverables checklist

- [x] Public GitHub repository
- [x] Streamlit application source
- [x] Setup and usage instructions
- [ ] Deploy and verify the live demo
- [ ] Record a demo video
- [ ] Capture screenshots of the working app and evaluation results
- [ ] Add final implementation/testing notes after validation

## Limitations

- Dataset examples are SMS messages; performance may differ on modern messaging apps, other languages, or new scam styles.
- TF-IDF and Logistic Regression learn patterns in the training set and can make false positives or false negatives.
- Model confidence is not a calibrated measure of real-world safety.
- Never paste passwords, OTPs, personal data, or confidential messages into a demo.
