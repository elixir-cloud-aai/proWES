from pathlib import Path

from connexion import App
from flask import current_app
from foca.foca import foca

from pro_wes.ga4gh.wes.routes.service_info import ServiceInfo
from pro_wes.exceptions import NotFound


def init_app() -> App:
    app = foca(Path(__file__).resolve().parent / "config.yaml")
    with app.app.app_context():
        service_info = ServiceInfo()
        try:
            service_info = service_info.get_service_info()
        except NotFound:
            service_info.set_service_info(
                data=current_app.config['FOCA'].endpoints['service_info']
            )
    return app


def run_app(app: App) -> None:
    app.run(port=app.port)


if __name__ == '__main__':
    app = init_app()
    run_app(app)
