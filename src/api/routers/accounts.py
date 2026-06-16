"""Account management routes."""

import asyncio
import uuid
from typing import Callable
from fastapi import FastAPI, HTTPException

from ..schemas.accounts import (
    AccountOut,
    RegisterRequest,
    RegisterResponse,
    DuckMailVerifyRequest,
    LabelUpdate,
)


def register_account_routes(
    app: FastAPI,
    list_accounts: Callable,
    save_account: Callable,
    delete_account: Callable,
    update_label: Callable,
    register_auto: Callable,
    register_duckmail_init: Callable,
    register_duckmail_verify: Callable,
):
    """Register account management routes."""

    @app.get("/api/accounts", response_model=list[AccountOut])
    async def api_list_accounts():
        return await list_accounts()

    @app.post("/api/accounts/register", response_model=RegisterResponse)
    async def api_register(body: RegisterRequest):
        svc = body.mail_service.lower()

        if svc == "mailtm":
            try:
                data = await register_auto()
                return RegisterResponse(done=True, account=AccountOut(**data))
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))

        elif svc == "duckmail":
            try:
                pending_data = await register_duckmail_init()
                return RegisterResponse(
                    done=False,
                    pending_id=pending_data["pending_id"],
                    email=pending_data["email"],
                    inbox_url=pending_data["inbox_url"],
                )
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
        else:
            raise HTTPException(status_code=400, detail="Unknown mail_service")

    @app.post("/api/accounts/verify-duckmail", response_model=RegisterResponse)
    async def api_verify_duckmail(body: DuckMailVerifyRequest):
        try:
            data = await register_duckmail_verify(body.pending_id, body.code)
            return RegisterResponse(done=True, account=AccountOut(**data))
        except ValueError as e:
            raise HTTPException(status_code=404, detail=str(e))
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))

    @app.delete("/api/accounts/{user_id}")
    async def api_delete_account(user_id: str):
        ok = await delete_account(user_id)
        if not ok:
            raise HTTPException(status_code=404, detail="Account not found")
        return {"ok": True}

    @app.patch("/api/accounts/{user_id}/label")
    async def api_update_label(user_id: str, body: LabelUpdate):
        await update_label(user_id, body.label)
        return {"ok": True}
