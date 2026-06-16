"""Routers package."""

from .accounts import register_account_routes
from .chat import register_chat_routes
from .stats import register_stats_routes

__all__ = [
    "register_account_routes",
    "register_chat_routes",
    "register_stats_routes",
]
