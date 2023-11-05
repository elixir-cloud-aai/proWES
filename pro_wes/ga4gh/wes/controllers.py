"""Controller for GA4GH WES API endpoints."""

import logging
from typing import Dict, Literal, Optional, Tuple

from connexion import request
from foca.utils.logging import log_traffic

from pro_wes.ga4gh.wes.workflow_runs import WorkflowRuns
from pro_wes.ga4gh.wes.service_info import ServiceInfo

logger = logging.getLogger(__name__)

# pragma pylint: disable=invalid-name,unused-argument


@log_traffic
def GetServiceInfo() -> Dict:
    """Get information about this service.

    Controller for `GET /service-info`.

    Returns:
        Response object according to WES API schema `RunId`. Cf.
            https://github.com/ga4gh/workflow-execution-service-schemas/blob/c5406f1d3740e21b93d3ac71a4c8d7b874011519/openapi/workflow_execution_service.swagger.yaml#L373-441
    """
    service_info = ServiceInfo()
    return service_info.get_service_info()


@log_traffic
def PostServiceInfo(**kwargs) -> Tuple[None, Literal["201"], Optional[dict[str, str]]]:
    """Set information about this service.

    Controller for `POST /service-info`.

    Args:
        **kwargs: Additional keyword arguments passed along with request.

    Returns:
        An empty `201` response with headers.
    """
    service_info = ServiceInfo()
    service_info.set_service_info(data=request.json)
    headers = None
    return (None, "201", headers)


@log_traffic
def RunWorkflow(*args, **kwargs) -> Dict[str, str]:
    """Start workflow run.

    Controller for `POST /runs`.

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


@log_traffic
def ListRuns(*args, **kwargs) -> Dict:
    """Return list of workflow runs.

    Controller for `GET /runs`.

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


@log_traffic
def GetRunLog(run_id, *args, **kwargs) -> Dict:
    """Return detailed information about a workflow run.

    Controller for `GET /runs/{run_id}`.

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


@log_traffic
def GetRunStatus(run_id, *args, **kwargs) -> Dict:
    """Return status information about a workflow run.

    Controller for `GET /runs/{run_id}/status`.

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


@log_traffic
def CancelRun(run_id, *args, **kwargs) -> Dict[str, str]:
    """Cancel workflow run.

    Controller for `POST /runs/{run_id}/cancel`.

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
