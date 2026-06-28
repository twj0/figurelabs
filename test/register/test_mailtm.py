"""Test registration with Mail.tm service."""

import sys

from src.register import FigureLabsRegistration, MailTmService


class FakeMailService:
    def create_account(self):
        return "generated@example.test", "mail-token"

    def get_messages(self, email: str, token: str):
        return []

    def extract_verification_code(self, messages: list):
        return None


class RegistrationWithEmptyLoginEmail(FigureLabsRegistration):
    def send_verification_code(self, email: str) -> str:
        return "code-id"

    def wait_for_verification_code(self, email: str, token: str, timeout: int = 60) -> str:
        return "123456"

    def login(self, email: str, code: str, code_id: str):
        return {
            "userId": "user-1",
            "accessToken": "access-token",
            "refreshToken": "refresh-token",
            "expiresTime": 1,
            "email": "",
        }


def test_register_auto_uses_generated_email_when_login_email_is_empty():
    result = RegistrationWithEmptyLoginEmail(FakeMailService()).register_auto()

    assert result["email"] == "generated@example.test"


def run_mailtm_registration():
    """Test automated registration with Mail.tm."""
    print("=" * 60)
    print("Testing Mail.tm Automated Registration")
    print("=" * 60)

    mail_service = MailTmService()
    client = FigureLabsRegistration(mail_service)

    try:
        result = client.register_auto()

        print("\n✅ Test passed!")
        print(f"\nRegistered account:")
        print(f"  User ID: {result['userId']}")
        print(f"  Email: {result.get('email', 'N/A')}")
        print(f"  Access Token: {result['accessToken'][:20]}...")

        return True
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = run_mailtm_registration()
    sys.exit(0 if success else 1)
