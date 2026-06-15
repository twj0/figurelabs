"""Export client — resolves message status and dispatches to formats."""

from typing import Any, Dict, List, Optional

import requests

from . import formats
from ._session import BASE_URL, make_session


class ExportClient:
    """Download generated figures in PNG, JPG, SVG, or PPTX format."""

    def __init__(self, access_token: str):
        self.session: requests.Session = make_session(access_token)

    def get_message_status(self, message_id: str) -> Optional[Dict[str, Any]]:
        resp = self.session.get(
            f"{BASE_URL}/app-api/plot/chat/message/status",
            params={"messageId": message_id},
        )
        try:
            result = resp.json()
            if result["code"] == 0:
                return result["data"]
        except Exception:
            pass
        return None

    def get_png_urls(self, message_id: str) -> List[str]:
        status = self.get_message_status(message_id)
        if not status:
            return []
        if status.get("status") != 1:
            print(f"[export] not ready (status={status.get('status')})")
            return []
        return status.get("fileUrl", [])

    def download(
        self,
        message_id: str,
        fmt: str = "png",
        output_dir: str = ".",
        filename: Optional[str] = None,
    ) -> Optional[str]:
        urls = self.get_png_urls(message_id)
        if not urls:
            return None
        return formats.download(self.session, urls[0], fmt, output_dir, filename)

    def download_all(
        self,
        message_id: str,
        fmts: List[str],
        output_dir: str = ".",
        filename: Optional[str] = None,
    ) -> Dict[str, Optional[str]]:
        urls = self.get_png_urls(message_id)
        if not urls:
            return {f: None for f in fmts}
        png_url = urls[0]
        return {
            f: formats.download(self.session, png_url, f, output_dir, filename)
            for f in fmts
        }
