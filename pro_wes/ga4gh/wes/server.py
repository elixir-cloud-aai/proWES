"""Controller for GA4GH WES API endpoints."""

import logging

from celery import current_app as celery_app
from connexion import request
from foca.utils.logging import log_traffic
from flask import current_app

#from pro_wes.ga4gh.wes.endpoints import (
#    cancel_run,
#    get_run_log,
#    get_run_status,
#    list_runs,
#    run_workflow,
#    get_service_info,
#)

# Get logger instance
logger = logging.getLogger(__name__)


# GET /runs/<run_id>
@log_traffic
def GetRunLog(run_id, *args, **kwargs):
    """Returns detailed run info."""
    return None
    response = get_run_log.get_run_log(
        config=current_app.config,
        run_id=run_id,
        *args,
        **kwargs
    )
    return response


# POST /runs/<run_id>/cancel
@log_traffic
def CancelRun(run_id, *args, **kwargs):
    """Cancels unfinished workflow run."""
    return None
    response = cancel_run.cancel_run(
        config=current_app.config,
        celery_app=celery_app,
        run_id=run_id,
        *args,
        **kwargs
    )
    return response


# GET /runs/<run_id>/status
@log_traffic
def GetRunStatus(run_id, *args, **kwargs):
    """Returns run status."""
    return None
    response = get_run_status.get_run_status(
        config=current_app.config,
        run_id=run_id,
        *args,
        **kwargs
    )
    return response


# GET /service-info
@log_traffic
def GetServiceInfo(*args, **kwargs):
    """Returns service info."""
    return None
    response = get_service_info.get_service_info(
        config=current_app.config,
        *args,
        **kwargs
    )
    return response


# GET /runs
@log_traffic
def ListRuns(*args, **kwargs):
    """Lists IDs and status of all workflow runs."""
    return None
    response = list_runs.list_runs(
        config=current_app.config,
        *args,
        **kwargs
    )
    return response


# POST /runs
@log_traffic
def RunWorkflow(*args, **kwargs):
    """Executes workflow."""
    return None
    response = run_workflow.run_workflow(
        config=current_app.config,
        form_data=request.form,
        *args,
        **kwargs
    )
    return response
