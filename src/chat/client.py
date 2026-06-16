"""FigureLabs.ai chat client."""

import re
import time
import urllib3
from typing import Any, Dict, Optional

import requests

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class FigureLabsChat:
    """FigureLabs.ai chat and conversation client."""

    BASE_URL = "https://chat.figurelabs.ai"

    def __init__(self, access_token: str):
        self.access_token = access_token
        self.session = requests.Session()
        self.session.headers.update(
            {
                "Authorization": f"Bearer {access_token}",
                "Origin": self.BASE_URL,
                "Referer": f"{self.BASE_URL}/",
            }
        )
        # The web client sends Access-Token as a cookie alongside the Bearer header.
        self.session.cookies.set("Access-Token", access_token, domain="chat.figurelabs.ai")
        self.session.verify = False

    def check_login(self) -> bool:
        url = f"{self.BASE_URL}/app-api/plot/member/checkLogin"
        result = self.session.get(url).json()
        print(f"[login] {result}")
        return result.get("data") is True

    def get_user_info(self) -> Optional[Dict[str, Any]]:
        result = self.session.get(f"{self.BASE_URL}/app-api/plot/member/info").json()
        if result["code"] == 0:
            return result["data"]
        return None

    def get_points_remaining(self) -> Optional[Dict[str, int]]:
        result = self.session.post(
            f"{self.BASE_URL}/app-api/plot/package/points/remaining", json={}
        ).json()
        if result["code"] == 0:
            return result["data"]
        return None

    def get_model_list(self, scene: str = "iiterature") -> Optional[list]:
        result = self.session.get(
            f"{self.BASE_URL}/app-api/plot/chat/model/list", params={"scene": scene}
        ).json()
        if result["code"] == 0:
            return result["data"]
        return None

    def create_session(self, title: str = "Chat Session", agent_id: int = 0) -> Optional[str]:
        result = self.session.post(
            f"{self.BASE_URL}/app-api/plot/chat/session/create",
            json={"title": title, "agentId": agent_id},
        ).json()
        if result["code"] == 0:
            session_id = result["data"]
            print(f"[session] {session_id}")
            return session_id
        return None

    def send_message(
        self,
        session_id: str,
        message: str,
        action_type: str = "NORMAL_CHAT",
        model_id: Optional[int] = None,
        ratio: Optional[str] = None,
        style: Optional[str] = None,
        first_message: bool = False,
        scene: str = "normal_chat",
    ) -> Optional[str]:
        """Send a message and return the message ID from the SSE response.

        Args:
            session_id: Session ID
            message: Prompt text
            action_type: NORMAL_CHAT or other action types
            model_id: Model ID (6=Nano Banana, 7=Nano Banana Pro, 10=Banana-2, 12=GPT Image 2)
            ratio: Image ratio (Auto, 16:9, 1:1, 4:3, ...)
            style: Style name (Flat, 3D, ...)
            first_message: True to include title in the request
            scene: Scene type (normal_chat, iiterature)

        Returns:
            Message ID string or None
        """
        files: Dict[str, Any] = {
            "actionType": (None, action_type),
            "sessionId": (None, session_id),
            "scene": (None, scene),
            "text": (None, message),
        }
        # HAR-confirmed: modelId=7 + ratio="16:9" works. ratio="Auto" is rejected for new accounts.
        if model_id is not None:
            files["modelId"] = (None, str(model_id))
        if ratio:
            files["ratio"] = (None, ratio)
        if style:
            files["style"] = (None, style)
        if first_message:
            files["firstMessage"] = (None, "true")
            files["title"] = (None, message[:80])

        resp = self.session.post(
            f"{self.BASE_URL}/app-api/plot/chat/message",
            files=files,
            stream=True,
            timeout=60,
        )
        if resp.status_code != 200:
            print(f"[send] HTTP {resp.status_code}")
            return None

        # Read SSE lines until we find the messageId, then stop — don't buffer the whole stream.
        message_id = None
        for line in resp.iter_lines(decode_unicode=True):
            if not line:
                continue
            match = re.search(r'"messageId":"(\d+)"', line)
            if match:
                message_id = match.group(1)
                break
        if message_id:
            print(f"[message] {message_id}")
            return message_id
        return None

    def get_message_status(self, message_id: str) -> Optional[Dict[str, Any]]:
        """Return raw status data dict for a message."""
        resp = self.session.get(
            f"{self.BASE_URL}/app-api/plot/chat/message/status",
            params={"messageId": message_id},
        )
        try:
            result = resp.json()
            if result["code"] == 0:
                return result["data"]
        except Exception:
            pass
        return None

    def get_thinking_status(self, message_id: str) -> Optional[Dict[str, Any]]:
        """Return thinking/step status for a message in progress."""
        resp = self.session.get(
            f"{self.BASE_URL}/app-api/plot/chat/message/thinking/status",
            params={"messageId": message_id},
        )
        try:
            result = resp.json()
            if result["code"] == 0:
                return result["data"]
        except Exception:
            pass
        return None

    def wait_for_completion(
        self, message_id: str, timeout: int = 180, poll_interval: int = 3
    ) -> Optional[Dict[str, Any]]:
        """Poll until generation completes (status=1) or fails (status=2).

        Args:
            message_id: Message ID
            timeout: Max seconds to wait
            poll_interval: Seconds between polls

        Returns:
            Final status data dict (with fileUrl list) or None on failure/timeout
        """
        deadline = time.time() + timeout
        n = 0
        print(f"[wait] message {message_id}")
        while time.time() < deadline:
            n += 1
            status = self.get_message_status(message_id)
            if status:
                s = status.get("status", 0)
                if s == 1 and status.get("fileUrl"):
                    print(f"[wait] done after {n} polls")
                    return status
                if s == 2:
                    print(f"[wait] generation failed")
                    return None
                if n % 5 == 0:
                    thinking = self.get_thinking_status(message_id)
                    step = thinking and f"{thinking['currentStep']}/{thinking['totalSteps']} {thinking['stepName']}"
                    print(f"[wait] poll {n} status={s} {step or ''}")
            time.sleep(poll_interval)
        print(f"[wait] timeout after {n} polls")
        return None

    def expand_prompt(self, message: str) -> Optional[str]:
        """Call /message/expand to get an AI-enhanced version of the prompt.

        HAR-confirmed: POST /app-api/plot/chat/message/expand?message=<text>
        Returns the expanded prompt string or None on failure.
        """
        resp = self.session.post(
            f"{self.BASE_URL}/app-api/plot/chat/message/expand",
            params={"message": message},
        )
        try:
            result = resp.json()
            if result.get("code") == 0:
                return result["data"]
        except Exception:
            pass
        return None

    def get_session_history(self, page: int = 1, page_size: int = 20) -> Optional[Dict]:
        result = self.session.post(
            f"{self.BASE_URL}/app-api/plot/chat/session/history",
            params={"pageNo": page, "pageSize": page_size},
        ).json()
        if result["code"] == 0:
            return result["data"]
        return None
