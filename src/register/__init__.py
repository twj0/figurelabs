"""Registration module for FigureLabs.ai."""

from .client import FigureLabsRegistration
from .mail_service import MailTmService, DuckMailService, TempMailService

__all__ = [
    "FigureLabsRegistration",
    "MailTmService",
    "DuckMailService",
    "TempMailService",
]
