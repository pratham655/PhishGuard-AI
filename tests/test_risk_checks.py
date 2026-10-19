import unittest

from risk_checks import detect_risk_signals


class RiskChecksTests(unittest.TestCase):
    def test_otp_request_is_flagged(self):
        text = "I am from customer support. Send me the verification code you just received."
        self.assertTrue(any("OTP" in signal or "verification code" in signal for signal in detect_risk_signals(text)))

    def test_delivery_payment_is_flagged(self):
        text = "Your parcel is on hold due to an unpaid customs charge. Pay immediately to avoid return."
        self.assertTrue(detect_risk_signals(text))

    def test_upfront_job_fee_is_flagged(self):
        text = "A job is available, but pay a registration fee before your interview."
        self.assertTrue(detect_risk_signals(text))

    def test_link_and_account_action_is_flagged(self):
        text = "Your account is locked. Verify your account here https://example.com/login"
        self.assertTrue(detect_risk_signals(text))

    def test_benign_college_reminder_is_not_flagged(self):
        text = "Bring your calculator and lab record for tomorrow's practical examination."
        self.assertEqual(detect_risk_signals(text), [])

    def test_benign_family_message_is_not_flagged(self):
        text = "Mom, I'll reach home around 7 pm. Please keep dinner ready if possible."
        self.assertEqual(detect_risk_signals(text), [])


if __name__ == "__main__":
    unittest.main()
