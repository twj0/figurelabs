"""FigureLabs.ai registration client."""

import time
import urllib3
import uuid
from typing import Any, Dict, Optional

import requests

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

from .mail_service import TempMailService


class FigureLabsRegistration:

    BASE_URL = "https://api.figurelabs.ai"

    def __init__(self, mail_service: Optional[TempMailService] = None):
        self.session = requests.Session()
        self.session.verify = False
        self.device_id = str(uuid.uuid4())
        self.mail_service = mail_service
        self.access_token: Optional[str] = None
        self.refresh_token: Optional[str] = None
        self.user_id: Optional[str] = None

    def send_verification_code(self, email: str) -> str:
        """Send verification code to email.

        Args:
            email: Target email address

        Returns:
            Code ID for verification
        """
        url = f"{self.BASE_URL}/app-api/plot/member/mail"
        data = {"email": email}

        print(f"\n[1/3] Sending verification code to {email}...")

        response = self.session.post(url, data=data)
        result = response.json()

        if result["code"] == 0:
            code_id = result["data"]
            print(f"✓ Verification code sent, Code ID: {code_id}")
            return code_id
        else:
            raise Exception(f"Failed to send verification code: {result}")

    def wait_for_verification_code(
        self, email: str, token: str, timeout: int = 60
    ) -> Optional[str]:
        """Wait for and extract verification code from email.

        Args:
            email: Email address to check
            token: Email service token
            timeout: Maximum wait time in seconds

        Returns:
            Verification code if found, None otherwise
        """
        print(f"\n[2/3] Waiting for verification code (max {timeout}s)...")

        start_time = time.time()
        while time.time() - start_time < timeout:
            messages = self.mail_service.get_messages(email, token)

            if messages:
                code = self.mail_service.extract_verification_code(messages)
                if code:
                    print(f"✓ Verification code received: {code}")
                    return code

            time.sleep(3)

        print("✗ Timeout waiting for verification code")
        return None

    def login(self, email: str, code: str, code_id: str) -> Dict[str, Any]:
        """Login or register using verification code.

        Args:
            email: Email address
            code: 6-digit verification code
            code_id: Code ID from send_verification_code

        Returns:
            User data including tokens
        """
        url = f"{self.BASE_URL}/app-api/plot/member/login"

        payload = {
            "email": email,
            "password": code,
            "codeId": code_id,
            "deviceId": self.device_id,
            "deviceType": "desktop",
            "os": "Windows",
            "browser": "Python",
            "referringDomain": "$direct",
        }

        print(f"\n[3/3] Submitting verification code, logging in...")

        response = self.session.post(url, json=payload)
        result = response.json()

        if result["code"] == 0:
            data = result["data"]
            self.access_token = data["accessToken"]
            self.refresh_token = data["refreshToken"]
            self.user_id = data["userId"]

            if data["isNewUser"]:
                print(f"\n{'='*60}")
                print(f"🎉 Registration successful!")
            else:
                print(f"\n{'='*60}")
                print(f"✓ Login successful!")

            print(f"{'='*60}")
            print(f"User ID:       {data['userId']}")
            print(f"Access Token:  {data['accessToken']}")
            print(f"Refresh Token: {data['refreshToken']}")
            expires_str = time.strftime(
                "%Y-%m-%d %H:%M:%S", time.localtime(data["expiresTime"] / 1000)
            )
            print(f"Expires Time:  {expires_str}")
            print(f"{'='*60}\n")

            return data
        else:
            raise Exception(f"Login failed: {result}")

    def register_auto(self) -> Dict[str, Any]:
        """Automated registration flow (Mail.tm only).

        Returns:
            User data including tokens
        """
        if not self.mail_service:
            raise ValueError("Mail service not configured")

        email, token = self.mail_service.create_account()
        code_id = self.send_verification_code(email)
        code = self.wait_for_verification_code(email, token)

        if not code:
            raise Exception("Failed to retrieve verification code automatically")

        return self.login(email, code, code_id)

    def register_manual(self, email: Optional[str] = None) -> Dict[str, Any]:
        """Manual registration flow with code input.

        Args:
            email: Email address (generated if not provided)

        Returns:
            User data including tokens
        """
        if not email and self.mail_service:
            email, token = self.mail_service.create_account()
            print(f"\nCheck email {email} for verification code")

        if not email:
            raise ValueError("Email address required")

        code_id = self.send_verification_code(email)
        code = input("\nEnter verification code: ").strip()

        return self.login(email, code, code_id)
