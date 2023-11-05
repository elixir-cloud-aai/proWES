"""Controller for GA4GH WES API endpoints."""

import logging
from typing import (
    Dict,
    Tuple,
)

from connexion import request
from foca.utils.logging import log_traffic

from pro_wes.ga4gh.wes.workflow_runs import WorkflowRuns
from pro_wes.ga4gh.wes.service_info import ServiceInfo

logger = logging.getLogger(__name__)


# controller for `GET /service-info`
@log_traffic
def GetServiceInfo() -> Dict:
    """Get information about this service.

    Returns:
        Response object according to WES API schema `RunId`. Cf.
            https://github.com/ga4gh/workflow-execution-service-schemas/blob/c5406f1d3740e21b93d3ac71a4c8d7b874011519/openapi/workflow_execution_service.swagger.yaml#L373-441
    """
    service_info = ServiceInfo()
    return service_info.get_service_info()


# controller for `POST /service-info``
@log_traffic
def postServiceInfo(**kwargs) -> Tuple[None, str, Dict]:
    """Set information about this service.

    Args:
        **kwargs: Additional keyword arguments passed along with request.

    Returns:
        An empty `201` response with headers.
    """
    service_info = ServiceInfo()
    headers = service_info.set_service_info(data=request.json)
    return (None, "201", headers)


# controller for `POST /runs`
@log_traffic
def RunWorkflow(*args, **kwargs) -> Dict[str, str]:
    """Start workflow run.

    Args:
        *args: Positional arguments passed along with request.
        **kwargs: Additional keyword arguments passed along with request.

    Returns:
        Response object according to WES API schema `RunId`. Cf.
            https://github.com/ga4gh/workflow-execution-service-schemas/blob/c5406f1d3740e21b93d3ac71a4c8d7b874011519/openapi/workflow_execution_service.swagger.yaml#L579-584
    """
    workflow_run = WorkflowRuns()
    response = workflow_run.run_workflow(
        request=request,
        **kwargs,
    )
    return response


# controller for `GET /runs`
@log_traffic
def ListRuns(*args, **kwargs) -> Dict:
    """Return list of workflow runs.

    Args:
        *args: Positional arguments passed along with request.
        **kwargs: Keyword arguments passed along with request.

    Returns:
        Response object according to WES API schema `RunListResponse`. Cf.
            https://github.com/ga4gh/workflow-execution-service-schemas/blob/c5406f1d3740e21b93d3ac71a4c8d7b874011519/openapi/workflow_execution_service.swagger.yaml#L495-L510
    """
    workflow_run = WorkflowRuns()
    response = workflow_run.list_runs(**kwargs)
    return response


# controller for `GET /runs/{run_id}`
@log_traffic
def GetRunLog(run_id, *args, **kwargs) -> Dict:
    """Return detailed information about a workflow run.

    Args:
        run_id: Workflow run identifier.
        *args: Positional arguments passed along with request.
        **kwargs: Additional keyword arguments passed along with request.

    Returns:
        Response object according to WES API schema `RunLog`. Cf.
            https://github.com/ga4gh/workflow-execution-service-schemas/blob/c5406f1d3740e21b93d3ac71a4c8d7b874011519/openapi/workflow_execution_service.swagger.yaml#L511-L533

    Raises:
        pro_wes.exceptions.Forbidden: The requester is not allowed to
            access the resource.
        pro_wes.exceptions.RunNotFound: The requested workflow run is not
            available.
    """
    workflow_run = WorkflowRuns()
    response = workflow_run.get_run_log(run_id=run_id, **kwargs)
    return response


# controller for `GET /runs/{run_id}/status`
@log_traffic
def GetRunStatus(run_id, *args, **kwargs) -> Dict:
    """Return status information about a workflow run.

    Args:
        run_id: Workflow run identifier.
        *args: Positional arguments passed along with request.
        **kwargs: Additional keyword arguments passed along with request.

    Returns:
        Response object according to WES API schema `RunStatus`. Cf.
            https://github.com/ga4gh/workflow-execution-service-schemas/blob/c5406f1d3740e21b93d3ac71a4c8d7b874011519/openapi/workflow_execution_service.swagger.yaml#L585-L594

    Raises:
        pro_wes.exceptions.Forbidden: The requester is not allowed to
            access the resource.
        pro_wes.exceptions.RunNotFound: The requested workflow run is not
            available.
    """
    workflow_run = WorkflowRuns()
    response = workflow_run.get_run_status(run_id=run_id, **kwargs)
    return response


# controller for `POST /runs/{run_id}/cancel`
@log_traffic
def CancelRun(run_id, *args, **kwargs) -> Dict[str, str]:
    """Cancel workflow run.

    Args:
        run_id: Workflow run identifier.
        *args: Positional arguments passed along with request.
        **kwargs: Additional keyword arguments passed along with request.

    Returns:
        Response object according to WES API schema `RunId`. Cf.
            https://github.com/ga4gh/workflow-execution-service-schemas/blob/c5406f1d3740e21b93d3ac71a4c8d7b874011519/openapi/workflow_execution_service.swagger.yaml#L579-L584

    Raises:
        pro_wes.exceptions.Forbidden: The requester is not allowed to
            access the resource.
        pro_wes.exceptions.RunNotFound: The requested workflow run is not
            available.
    """
    workflow_run = WorkflowRuns()
    response = workflow_run.cancel_run(run_id=run_id, **kwargs)
    return response
