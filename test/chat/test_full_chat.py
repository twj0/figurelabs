"""Full chat test with AI response waiting."""

import sys

from src.chat import FigureLabsChat


def run_full_chat(access_token: str) -> bool:
    """Complete chat test including waiting for AI response.

    Args:
        access_token: Access token

    Returns:
        True if entire conversation succeeds, False otherwise
    """
    print("=" * 60)
    print("FigureLabs.ai Full Chat Test")
    print("=" * 60)

    client = FigureLabsChat(access_token)

    # Check login
    if not client.check_login():
        print("❌ Login status invalid")
        return False

    # Get user info
    user_info = client.get_user_info()
    if not user_info:
        return False

    # Get points
    client.get_points_remaining()

    # Get models
    client.get_model_list()

    # Create session
    session_id = client.create_session()
    if not session_id:
        return False

    # Send message
    test_message = "Hello! Can you introduce yourself?"
    message_id = client.send_message(session_id, test_message)

    if not message_id:
        print("❌ Failed to send message")
        return False

    # Wait for response
    response = client.wait_for_response(message_id, timeout=90)

    if response:
        print("\n" + "=" * 60)
        print("✅ Full chat test passed!")
        print("=" * 60)
        return True
    else:
        print("\n" + "=" * 60)
        print("❌ Chat test failed (timeout or error)")
        print("=" * 60)
        return False


if __name__ == "__main__":
    test_token = "2a2d514100904fa884edc20b3927fff3"

    if len(sys.argv) > 1:
        test_token = sys.argv[1]

    print(f"Using token: {test_token[:20]}...\n")

    success = run_full_chat(test_token)
    sys.exit(0 if success else 1)
