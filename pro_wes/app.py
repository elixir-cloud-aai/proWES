from pathlib import Path

from connexion import App
from foca.foca import foca

from pro_wes.ga4gh.wes.endpoints.service_info import RegisterServiceInfo


def init_app() -> App:
    app = foca(Path(__file__).resolve().parent / "config.yaml")
    return app


def run_app(app: App) -> None:
    with app.app.app_context():
        service_info = RegisterServiceInfo()
        service_info.set_service_info_from_config()
    app.run(port=app.port)


if __name__ == '__main__':
    app = init_app()
    run_app(app)
