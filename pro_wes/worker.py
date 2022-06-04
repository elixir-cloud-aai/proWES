"""Entry point for Celery workers."""

from foca.factories.celery_app import create_celery_app

from pro_wes.app import init_app


# Source application configuration
flask_app = init_app().app

# Create Celery app
celery = create_celery_app(app=flask_app)
