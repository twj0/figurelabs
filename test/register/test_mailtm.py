"""Test registration with Mail.tm service."""

import sys

from src.register import FigureLabsRegistration, MailTmService


def test_mailtm_registration():
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
    success = test_mailtm_registration()
    sys.exit(0 if success else 1)
