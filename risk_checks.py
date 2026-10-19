import re


def detect_risk_signals(text: str) -> list[str]:
    """Return transparent warning signs for selected social-engineering patterns.

    These heuristic rules supplement the ML classifier. They are not a trained
    model, do not establish intent, and must not be treated as a security verdict.
    """
    text_lower = text.lower()
    signals: list[str] = []
    patterns = [
        (
            r"\b(?:send|share|tell|reply with|provide|give me|forward)\b.{0,60}\b(?:otp|one[- ]time password|verification code|security code|pin|password)\b"
            r"|\b(?:otp|one[- ]time password|verification code|security code|pin|password)\b.{0,60}\b(?:send|share|reply|provide|give me|forward)\b",
            "Requests an OTP, PIN, password, or verification code",
        ),
        (
            r"\b(?:pay|payment|fee|charge|transfer)\b.{0,65}\b(?:release|claim|prize|parcel|package|customs|delivery|reward)\b"
            r"|\b(?:customs|parcel|package|delivery|prize|reward)\b.{0,65}\b(?:pay|payment|fee|charge|unpaid|transfer)\b",
            "Requests payment connected to a prize, reward, or delivery",
        ),
        (
            r"\b(?:job|employment|salary|position|work from home)\b.{0,80}\b(?:registration fee|deposit|pay upfront|processing fee|training fee)\b"
            r"|\b(?:registration fee|deposit|processing fee|training fee)\b.{0,80}\b(?:job|employment|salary|position|work from home)\b",
            "Requests an upfront fee related to a job offer",
        ),
        (
            r"\b(?:account|bank|card|wallet)\b.{0,65}\b(?:suspended|blocked|restricted|will be closed|locked)\b.{0,80}\b(?:click|verify|reply|send|provide|login|log in)\b"
            r"|\b(?:click|verify|reply|send|provide|login|log in)\b.{0,80}\b(?:account|bank|card|wallet)\b.{0,65}\b(?:suspended|blocked|restricted|locked)\b",
            "Combines an account-threat claim with a request to act",
        ),
        (
            r"https?://\S+.{0,100}\b(?:verify|login|log in|reset password|confirm account|claim prize|update payment)\b"
            r"|\b(?:verify|login|log in|reset password|confirm account|claim prize|update payment)\b.{0,100}https?://\S+",
            "Combines a web link with an account, credential, payment, or prize action",
        ),
        (
            r"\b(?:install|download)\b.{0,55}\b(?:remote access|screen sharing|support app|apk|application)\b.{0,70}\b(?:bank|account|payment|refund|support)\b"
            r"|\b(?:bank|account|payment|refund|support)\b.{0,70}\b(?:install|download)\b.{0,55}\b(?:remote access|screen sharing|support app|apk|application)\b",
            "Suggests installing an app in a financial or account-support context",
        ),
    ]
    for pattern, description in patterns:
        if re.search(pattern, text_lower, re.DOTALL):
            signals.append(description)
    return signals
