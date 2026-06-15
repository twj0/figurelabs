"""Temporary email service implementations."""

import re
import uuid
from typing import Optional

import requests


class TempMailService:
    """Base class for temporary email services."""

    def create_account(self) -> tuple[str, str]:
        """Create email account, return (email, token/password)."""
        raise NotImplementedError

    def get_messages(self, email: str, token: str) -> list:
        """Get message list."""
        raise NotImplementedError

    def extract_verification_code(self, messages: list) -> Optional[str]:
        """Extract verification code from messages."""
        raise NotImplementedError


class MailTmService(TempMailService):
    """Mail.tm temporary email service with full automation."""

    BASE_URL = "https://api.mail.tm"

    def __init__(self):
        self.session = requests.Session()

    def create_account(self) -> tuple[str, str]:
        """Create Mail.tm account."""
        domains_response = self.session.get(f"{self.BASE_URL}/domains")
        domains = domains_response.json()["hydra:member"]
        domain = domains[0]["domain"]

        username = f"test_{uuid.uuid4().hex[:8]}"
        email = f"{username}@{domain}"
        password = uuid.uuid4().hex

        account_data = {"address": email, "password": password}
        response = self.session.post(f"{self.BASE_URL}/accounts", json=account_data)

        if response.status_code == 201:
            print(f"✓ Mail.tm account created: {email}")

            token_response = self.session.post(f"{self.BASE_URL}/token", json=account_data)
            token = token_response.json()["token"]

            return email, token
        else:
            raise Exception(f"Failed to create Mail.tm account: {response.text}")

    def get_messages(self, email: str, token: str) -> list:
        """Get message list."""
        headers = {"Authorization": f"Bearer {token}"}
        response = self.session.get(f"{self.BASE_URL}/messages", headers=headers)

        if response.status_code == 200:
            return response.json()["hydra:member"]
        return []

    def extract_verification_code(self, messages: list) -> Optional[str]:
        """Extract 6-digit verification code from messages."""
        for msg in messages:
            subject = msg.get("subject", "")
            intro = msg.get("intro", "")

            pattern = r"\b\d{6}\b"
            match = re.search(pattern, subject + " " + intro)
            if match:
                return match.group(0)

        return None


class DuckMailService(TempMailService):
    """DuckMail temporary email service (manual verification)."""

    def create_account(self) -> tuple[str, str]:
        """Generate DuckMail address (no registration needed)."""
        username = f"test_{uuid.uuid4().hex[:10]}"
        email = f"{username}@duckmail.sbs"

        print(f"✓ DuckMail address generated: {email}")
        print(f"  Visit https://duckmail.sbs/{username} to view messages")

        return email, username

    def get_messages(self, email: str, token: str) -> list:
        """DuckMail has no public API, manual checking required."""
        print(f"\nVisit: https://duckmail.sbs/{token}")
        print("Check verification code manually")
        return []

    def extract_verification_code(self, messages: list) -> Optional[str]:
        """Manual input required."""
        return None
