from pathlib import Path

from foca.foca import foca

from pro_wes.ga4gh.wes.endpoints.service_info import RegisterServiceInfo


def main():

    # initialize app
    app = foca(Path(__file__).resolve().parent / "config.yaml")

    # register service info
    with app.app.app_context():
        service_info = RegisterServiceInfo()
        service_info.set_service_info_from_config()

    # start app
    app.run(port=app.port)


if __name__ == '__main__':
    main()
