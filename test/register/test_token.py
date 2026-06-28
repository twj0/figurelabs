"""Test token verification."""

import sys

import requests


def run_token_verification(access_token: str) -> bool:
    """Verify token and retrieve user information.

    Args:
        access_token: Access token to verify

    Returns:
        True if valid, False otherwise
    """
    url = "https://chat.figurelabs.ai/app-api/plot/member/info"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }

    print(f"Verifying token: {access_token[:20]}...")

    response = requests.get(url, headers=headers)
    result = response.json()

    if result["code"] == 0:
        data = result["data"]
        print("\n✅ Token valid!")
        print(f"\nUser information:")
        print(f"  ID: {data['id']}")
        print(f"  Name: {data.get('name', 'N/A')}")
        print(f"  Email: {data.get('email', 'N/A')}")
        print(f"  Subscription: {data.get('subscriptionType', 'N/A')}")
        print(f"  Is Subscribed: {data.get('isSubscribed', False)}")
        print(f"  Created: {data.get('createTime', 'N/A')}")
        return True
    else:
        print(f"\n❌ Token invalid: {result}")
        return False


if __name__ == "__main__":
    # Test token from previous registration
    test_token = "2a2d514100904fa884edc20b3927fff3"

    if len(sys.argv) > 1:
        test_token = sys.argv[1]

    success = run_token_verification(test_token)
    sys.exit(0 if success else 1)
