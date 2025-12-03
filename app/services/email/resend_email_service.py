import resend

from typing import List, Optional



class ResendEmailService:
    def __init__(self, api_key: str, sender: str):
        resend.api_key = api_key
        self.sender = sender
    async def send_email(
        self,
        to: str,
        subject: str,
        html: str,
        cc: Optional[List[str]] = None,
        bcc: Optional[List[str]] = None

    ):
        return resend.Emails.send({
            "from": self.sender,
            "to": [to],
            "subject": subject,
            "html": html,
            "cc": cc or [],
            "bcc": bcc or []

        })

