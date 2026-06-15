import urllib3
import requests

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

BASE_URL = "https://chat.figurelabs.ai"


def make_session(access_token: str) -> requests.Session:
    s = requests.Session()
    s.headers.update(
        {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
            "Origin": BASE_URL,
            "Referer": f"{BASE_URL}/",
        }
    )
    s.cookies.set("Access-Token", access_token, domain="chat.figurelabs.ai")
    s.verify = False
    return s
