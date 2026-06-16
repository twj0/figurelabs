"""Application factory and configuration."""

from dataclasses import dataclass
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware
import os


@dataclass(frozen=True)
class AppFactorySettings:
    frontend_origin: str
    allow_all_origins: bool
    session_secret_key: str
    session_expire_hours: int
    static_dir: str = "static"


def create_http_app(settings: AppFactorySettings) -> FastAPI:
    app = FastAPI(title="FigureLabs AI", docs_url=None, redoc_url=None)
    _configure_cors(app, settings)
    _mount_frontend_assets(app, settings.static_dir)
    _configure_session(app, settings)
    return app


def _configure_cors(app: FastAPI, settings: AppFactorySettings) -> None:
    if settings.allow_all_origins and not settings.frontend_origin:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=False,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        return

    if settings.frontend_origin:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=[settings.frontend_origin],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )


def _mount_frontend_assets(app: FastAPI, static_dir: str) -> None:
    if not os.path.exists(static_dir):
        return

    app.mount("/static", StaticFiles(directory=static_dir), name="static")

    assets_dir = os.path.join(static_dir, "assets")
    if os.path.exists(assets_dir):
        app.mount("/assets", StaticFiles(directory=assets_dir), name="assets")

    vendor_dir = os.path.join(static_dir, "vendor")
    if os.path.exists(vendor_dir):
        app.mount("/vendor", StaticFiles(directory=vendor_dir), name="vendor")


def _configure_session(app: FastAPI, settings: AppFactorySettings) -> None:
    app.add_middleware(
        SessionMiddleware,
        secret_key=settings.session_secret_key,
        max_age=settings.session_expire_hours * 3600,
        same_site="lax",
        https_only=False,
    )
