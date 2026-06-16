"""Pydantic schemas for accounts."""

from typing import Optional
from pydantic import BaseModel


class AccountOut(BaseModel):
    id: int
    user_id: str
    email: str
    access_token: str
    mail_service: str
    created_at: int
    label: Optional[str] = None
    expires_time: Optional[int] = None


class RegisterRequest(BaseModel):
    mail_service: str = "mailtm"


class RegisterResponse(BaseModel):
    done: bool
    account: Optional[AccountOut] = None
    pending_id: Optional[str] = None
    email: Optional[str] = None
    inbox_url: Optional[str] = None


class DuckMailVerifyRequest(BaseModel):
    pending_id: str
    code: str


class LabelUpdate(BaseModel):
    label: str
