"""proWES application entry point."""

from pathlib import Path

from connexion import App
from flask import current_app
from foca import Foca

from pro_wes.ga4gh.wes.service_info import ServiceInfo
from pro_wes.exceptions import NotFound


def init_app() -> App:
    """Initialize FOCA application.

    Returns:
        FOCA application.
    """
    foca = Foca(
        config_file=Path(__file__).resolve().parent / "config.yaml",
        custom_config_model="pro_wes.config_models.CustomConfig",
    )
    app = foca.create_app()
    _setup_first_start(app=app)
    return app


def _setup_first_start(app: App) -> None:
    """Set up application for first start."""
    with app.app.app_context():
        # create storage directory
        work_dir = Path(current_app.config.foca.custom.post_runs.storage_path.resolve())
        work_dir.mkdir(parents=True, exist_ok=True)
        # set service info
        service_info = ServiceInfo()
        try:
            service_info = service_info.get_service_info()
        except NotFound:
            service_info.set_service_info(
                data=current_app.config.foca.custom.service_info.dict()
            )


def run_app(app: App) -> None:
    """Run FOCA application."""
    app.run(port=app.port)


if __name__ == "__main__":
    foca_app = init_app()
    run_app(app=foca_app)
