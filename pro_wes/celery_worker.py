"""Celery worker entry point."""

from pathlib import Path

from celery import Celery
from foca import Foca  # type: ignore

foca = Foca(
    config_file=Path(__file__).resolve().parent / "config.yaml",
    custom_config_model="pro_wes.config_models.CustomConfig",
)
celery: Celery = foca.create_celery_app()
