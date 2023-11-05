"""Custom app config models."""

from typing import Optional
from pathlib import Path

from pydantic import BaseModel  # pylint: disable=no-name-in-module

from pro_wes.ga4gh.wes.models import ServiceInfoBase as ServiceInfo

# pragma pylint: disable=too-few-public-methods


class Defaults(BaseModel):
    """Model for global default parameters.
    Args:
        timeout: Timeout for outgoing requests. May be overridden by more
        specific parameters for each endpoint.

    Attributes:
        timeout: Timeout for outgoing requests. May be overridden by more
        specific parameters for each endpoint.
    """

    timeout: Optional[int] = 3


class PostRuns(BaseModel):
    """Model for controller config parameters for operation `POST /runs`.

    storage_path: Location inside the app container where storage will be
        mounted.
    db_insert_attempts: How many times the controller will create new run
        identifiers for inserting a new run document in the database. If
        exceeded, a `500/InternalServerError` will be returned.
    timeout_post: How long, in seconds, the application should attempt to reach
        a remote WES instance when sending a new workflow run request. Set to
        `None` to disable timing out.
    timeout_job: How long, in seconds, a background job tracking a workflow
        run is allowed to run. Set to `None` to disable timing out.
    polling_wait: How long, in seconds, the worker should wait in between
        status update calls.
    polling_attempts: How often the worker should attempt in a row to receive a
        valid run status response from the remote WES service until an error is
        raised and the job is set to state `SYSTEM_ERROR`. Once a valid
        response is obtained, the counter is reset to 1.
    """

    storage_path: Path = Path("/data")
    db_insert_attempts: int = 10
    id_charset: str = "string.ascii_uppercase + string.digits"
    id_length: int = 6
    timeout_post: Optional[int] = None
    timeout_job: Optional[int] = None
    polling_wait: float = 3
    polling_attempts: int = 100


class ListRuns(BaseModel):
    """Model for controller config parameters for operation `GET /runs`.

    Args:
        default_page_size: Default page size for response pagination.

    Attributes:
        default_page_size: Default page size for response pagination.
    """

    default_page_size: int = 5


class CustomConfig(BaseModel):
    """Custom app configuration.

    Args:
        defaults: Global configuration parameters.
        post_runs: Configuration parameters for operation `POST /runs`.
        list_runs: Configuration parameters for operation `GET /runs`.
        service_info: Configuration parameters for initiliazing the service
            info.

    Attributes:
        defaults: Global configuration parameters.
        post_runs: Configuration parameters for operation `POST /runs`.
        list_runs: Configuration parameters for operation `GET /runs`.
        service_info: Configuration parameters for initiliazing the service
            info.
    """

    defaults: Defaults = Defaults()
    post_runs: PostRuns = PostRuns()
    list_runs: ListRuns = ListRuns()
    service_info: ServiceInfo
