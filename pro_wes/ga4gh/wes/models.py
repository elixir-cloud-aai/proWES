"""proWES schema models."""

from enum import Enum, EnumMeta
from json import loads, JSONDecodeError
from pathlib import Path
from typing import Dict, List, Optional

from pydantic import (  # pylint: disable=no-name-in-module
    BaseModel,
    root_validator,
    validator,
)

from pro_wes.exceptions import NoSuitableEngine
from pro_wes.ga4gh.service_info.models import Service
from pro_wes.ga4gh.wes.service_info import ServiceInfo as ServiceInfoController

# pragma pylint: disable=too-few-public-methods


class MetaEnum(EnumMeta):
    """Metaclass for enumerators."""

    def __contains__(cls, item):
        try:
            cls(item)  # pylint: disable=no-value-for-parameter
        except ValueError:
            return False
        return True


class BaseEnum(Enum, metaclass=MetaEnum):
    """Base class for enumerators."""


class Attachment(BaseModel):
    """Model for workflow attachment.

    Args:
        filename: Name of the file as indicated in the run request.
        object: File object.
        path: Path to the file on the app's storage system.
    """

    filename: str
    object: bytes
    path: Path


class RunRequest(BaseModel):
    """Model for WES API `RunRequest` schema.

    Args:
        workflow_params: Workflow parameters. Cf.
            `pro_wes.api.20200806.4048014.workflow_execution_service.openapi.yaml`
        workflow_type: Workflow type. Cf.
            `pro_wes.api.20200806.4048014.workflow_execution_service.openapi.yaml`
        workflow_type_version: Workflow type version. Cf.
            `pro_wes.api.20200806.4048014.workflow_execution_service.openapi.yaml`
        tags: Tags. Cf.
            `pro_wes.api.20200806.4048014.workflow_execution_service.openapi.yaml`
        workflow_engine_parameters: Workflow engine parameters. Cf.
            `pro_wes.api.20200806.4048014.workflow_execution_service.openapi.yaml`
        workflow_url: Workflow URL. Cf.
            `pro_wes.api.20200806.4048014.workflow_execution_service.openapi.yaml`

    Attributes:
        workflow_params: Workflow parameters. Cf.
            `pro_wes.api.20200806.4048014.workflow_execution_service.openapi.yaml`
        workflow_type: Workflow type. Cf.
            `pro_wes.api.20200806.4048014.workflow_execution_service.openapi.yaml`
        workflow_type_version: Workflow type version. Cf.
            `pro_wes.api.20200806.4048014.workflow_execution_service.openapi.yaml`
        tags: Tags. Cf.
            `pro_wes.api.20200806.4048014.workflow_execution_service.openapi.yaml`
        workflow_engine_parameters: Workflow engine parameters. Cf.
            `pro_wes.api.20200806.4048014.workflow_execution_service.openapi.yaml`
        workflow_url: Workflow URL. Cf.
            `pro_wes.api.20200806.4048014.workflow_execution_service.openapi.yaml`

    Raises:
        pro_wes.exceptions.ValidationError: The class was instantianted with an
            illegal data type.
    """

    workflow_params: str
    workflow_type: str
    workflow_type_version: str
    tags: Optional[str] = "{}"
    workflow_engine_parameters: Optional[str] = "{}"
    workflow_url: str

    @validator(
        "workflow_type",
        "workflow_type_version",
        "workflow_url",
        always=True,
    )
    def required_str_field_not_empty(  # pylint: disable=no-self-argument
        cls,
        value: str,
    ) -> str:
        """Ensure that required strings are not empty.

        Args:
            value: Field value to be validated.

        Returns:
            Validated field value.

        Raises:
            ValueError: The value is either missing or constitutes an empty
                string.
        """
        if value == "" or value is None:
            raise ValueError("field required")
        return value

    @validator(
        "workflow_params",
        "tags",
        "workflow_engine_parameters",
        always=True,
    )
    def json_serialized_object_field_valid(  # pylint: disable=no-self-argument
        cls,
        value: str,
        field: str,
    ) -> str:
        """Ensure that a string can be JSON deserialized into an object.

        Due to limitations of OpenAPI, the form data fields indicated in the
        decorator were defined in the WES API specification as atomic strings,
        even though those strings are expected to be JSON-serialized
        representations of objects. This validator ensures that the values
        provided to these form fields can indeed be deserialized into objects.

        Note that the WES specification does not currently dictate how clients
        should indicate that no value is to be specified for optional fields.
        In order to maintain compatibility with upstream clients, while
        ensuring that a JSON deserializable representation is propagated,
        empty strings, missing field values and `null` for are set to the
        empty JSON string object '{}' for optional fields and cause a
        `ValueError` to be raised for required fields.

        Args:
            value: Field value to be validated.
            field: Name of field to be validated.

        Returns:
            Validated (and possibly sanitized) field value.

        Raises:
            ValueError: The value is required but it is either missing or does
                not represent any actual content.
            ValueError: The value could not be JSON deserialized.
            ValueError: The value could be JSON decoded, but the deserialized
                value does not represent an object/dictionary.
        """
        if value == "" or value == "null" or value is None:
            if field.name == "workflow_params":
                raise ValueError("field required")
            return "{}"
        try:
            decoded = loads(value)
        except JSONDecodeError as exc:
            raise ValueError("could not be JSON deserialized") from exc
        if not isinstance(decoded, dict):
            raise ValueError("could not be interpreted as object")
        return value

    @root_validator
    def workflow_type_and_version_supported(  # pylint: disable=no-self-argument
        cls,
        values: Dict,
    ) -> Dict:
        """Ensure that workflow type and version are supported by this service
        instance.

        Args:
            values (Dict): Field values dictionary.

        Returns:
            The validated field values.

        Raises:
            NoSuitableEngine: No suitable workflow engine known to process request.
        """
        service_info = ServiceInfoController().get_service_info(get_counts=False)
        type_versions = service_info["workflow_type_versions"]
        _type = values.get("workflow_type")
        version = values.get("workflow_type_version")
        if (
            _type not in type_versions
            or version not in type_versions[_type]["workflow_type_version"]
        ):
            raise NoSuitableEngine(
                f"No suitable workflow engine known for workflow type '{_type}' and"
                f" version '{version}'; supported workflow engines: {type_versions}"
            )
        return values


class Log(BaseModel):
    """Model for task log, including the log of the workflow engine itself.

    Cf. `pro_wes.api.20200806.4048014.workflow_execution_service.openapi.yaml`

    Attributes:
        cmd: List of executed commands.
        end_time: Time when the task stopped executing, in ISO 8601 format
            "%Y-%m-%dT%H:%M:%SZ".
        exit_code: Exit code of the task.
        name: The name of the task.
        start_time: Time when the task started executing, in ISO 8601 format
            "%Y-%m-%dT%H:%M:%SZ".
        stderr: A URL to retrieve standard error logs of the task.
        stdout: A URL to retrieve standard output logs of the task.
    """

    cmd: Optional[List[str]] = []
    end_time: Optional[str] = None
    exit_code: Optional[int] = None
    name: Optional[str] = None
    start_time: Optional[str] = None
    stderr: Optional[str] = None
    stdout: Optional[str] = None


class State(BaseEnum):
    """Enumerator for supported workflow run states.

    Cf. `pro_wes.api.20200806.4048014.workflow_execution_service.openapi.yaml`

    Attributes:
        UNKNOWN: The state of the task is unknown.
        QUEUED: The task is queued.
        INITIALIZING: The task has been assigned to a worker and is currently
            preparing to run.
        RUNNING: The task is running.
        PAUSED: The task is paused.
        COMPLETE: The task has completed running.
        EXECUTOR_ERROR: The task encountered an error in one of the Executor
            processes.
        SYSTEM_ERROR: The task was stopped due to a system error.
        CANCELED: The task was canceled by the user.
        CANCELING: The task was canceled by the user, and is in the process of
            stopping.
    """

    UNKNOWN = "UNKNOWN"
    QUEUED = "QUEUED"
    INITIALIZING = "INITIALIZING"
    RUNNING = "RUNNING"
    PAUSED = "PAUSED"
    COMPLETE = "COMPLETE"
    EXECUTOR_ERROR = "EXECUTOR_ERROR"
    SYSTEM_ERROR = "SYSTEM_ERROR"
    CANCELED = "CANCELED"
    CANCELING = "CANCELING"

    @property
    def is_finished(self):
        """Check if a state is among the set of finished states."""
        return self in (
            self.COMPLETE,
            self.EXECUTOR_ERROR,
            self.SYSTEM_ERROR,
            self.CANCELED,
        )

    @property
    def is_cancelable(self):
        """Check if a state is among the set of cancelable states."""
        return self in (
            self.QUEUED,
            self.INITIALIZING,
            self.RUNNING,
            self.PAUSED,
        )


class RunLog(BaseModel):
    """Model for entire workflow run log.

    Args:
        outputs: Name and destination of workflow outputs.
        request: Form data passed during original workflow run request.
        run_id: Unique identifier of workflow run.
        run_log: Log of workflow engine itself.
        state: State of workflow run.
        task_logs: List of workflow task/job logs.

    Attributes:
        outputs: Name and destination of workflow outputs.
        request: Form data passed during original workflow run request.
        run_id: Unique identifier of workflow run.
        run_log: Log of workflow engine itself.
        state: State of workflow run.
        task_logs: List of workflow task/job logs.
    """

    outputs: Optional[Dict] = None
    request: Optional[RunRequest] = None
    run_id: Optional[str] = None
    run_log: Optional[Log] = None
    state: State = State.UNKNOWN
    task_logs: Optional[List[Log]] = []

    class Config:
        """Pydantic model configuration."""

        use_enum_values = True


class WesEndpoint(BaseModel):
    """Model for information on the external WES endpoint to which the incoming
    workflow run request was relayed.

    Args:
        host: Host at which the WES API is served that is processing this
            request; note that this should include the path information but
            *not* the base path path defined in the WES API specification;
            e.g., specify https://my.wes.com/api if the actual API is hosted at
            https://my.wes.com/api/ga4gh/wes/v1.
        base_path: Override the default path suffix defined in the WES API
            specification, i.e., `/ga4gh/wes/v1`.
        run_id: Identifier for workflow run on external WES endpoint.

    Attributes:
        host: Host at which the WES API is served that is processing this
            request; note that this should include the path information but
            *not* the base path path defined in the WES API specification;
            e.g., specify https://my.wes.com/api if the actual API is hosted at
            https://my.wes.com/api/ga4gh/wes/v1.
        base_path: Override the default path suffix defined in the WES API
            specification, i.e., `/ga4gh/wes/v1`.
        run_id: Identifier for workflow run on external WES endpoint.
    """

    host: str
    base_path: Optional[str] = "/ga4gh/wes/v1"
    run_id: Optional[str] = None


class DbDocument(BaseModel):
    """Model for workflow run request database document.

    Args:
        attachments: Names of attached files.
        run_log: Complete logging information for workflow run.
        task_id: Identifier of worker task.
        user_id: Identifier of resource owner.
        wes_endpoint: Information about the endpoint to where the run request
            was forwarded.
        work_dir: Working directory for workflow run.

    Attributes:
        attachments: Names of attached files.
        run_log: Complete logging information for workflow run.
        task_id: Identifier of worker task.
        user_id: Identifier of resource owner.
        wes_endpoint: Information about the endpoint to where the run request
            was forwarded.
        work_dir: Working directory for workflow run.
    """

    attachments: List[Attachment] = []
    run_log: RunLog = RunLog()
    task_id: Optional[str] = None
    user_id: Optional[str] = None
    work_dir: Optional[Path] = None
    wes_endpoint: Optional[WesEndpoint] = None


class RunId(BaseModel):
    """Response model for `POST /runs`.

    Args:
        run_id: Workflow run identifier.

    Attributes:
        run_id: Workflow run identifier.
    """

    run_id: str


class RunStatus(BaseModel):
    """Response model for `GET /runs/{run_id}/status`.

    Args:
        run_id: Workflow run identifier.
        state: Workflow run state.

    Attributes:
        run_id: Workflow run identifier.
        state: Workflow run state.
    """

    run_id: str
    state: State


class ErrorResponse(BaseModel):
    """Response model for WES errors.

    Args:
        msg: Detailed error message.
        status_code: HTTP status code.

    Attributes:
        msg: Detailed error message.
        status_code: HTTP status code.
    """

    msg: Optional[str]
    status_code: int


class RunListResponse(BaseModel):
    """List of workflow runs that the service has processed or is processing.

    Args:
        runs: List of runs, indicating the run identifier and status for each.
        next_page_token: Token to receive the next page of results.
    """

    runs: Optional[List[RunStatus]] = []
    next_page_token: Optional[str]


class WorkflowTypeVersion(BaseModel):
    """Available workflow types supported by a given instance of the service.

    Args:
        workflow_type_version: List of one or more acceptable versions for the
            workflow type.
    """

    workflow_type_version: Optional[List[str]] = []


class DefaultWorkflowEngineParameter(BaseModel):
    """Model for default workflow engine parameters.

    Args:
        name: Parameter name.
        type: Parameter type.
        default_value: Stringified version of default parameter.

    Attributes:
        name: Parameter name.
        type: Parameter type.
        default_value: Stringified version of default parameter.
    """

    name: Optional[str]
    type: Optional[str]
    default_value: Optional[str]


class ServiceInfoWesBase(BaseModel):
    """Base model for WES-specific service info fields.

    Args:
        workflow_type_versions: Workflow types and versions supported by this
            service.
        supported_wes_versions: The version(s) of the WES schema supported by
            this service.
        supported_filesystem_protocols: The filesystem protocols supported by
            this service.
        workflow_engine_versions: Workflow engine versions supported by this
            service.
        default_workflow_engine_parameters: Default workflow engine parameters
            set by this service.
        auth_instructions_url: URL to web page with human-readable instructions
            on how to get an authorization token for use with this service.
        tags: Additional information about this service as key-value pairs.

    Attributes:
        workflow_type_versions: Workflow types and versions supported by this
            service.
        supported_wes_versions: The version(s) of the WES schema supported by
            this service.
        supported_filesystem_protocols: The filesystem protocols supported by
            this service.
        workflow_engine_versions: Workflow engine versions supported by this
            service.
        default_workflow_engine_parameters: Default workflow engine parameters
            set by this service.
        auth_instructions_url: URL to web page with human-readable instructions
            on how to get an authorization token for use with this service.
        tags: Additional information about this service as key-value pairs.
    """

    workflow_type_versions: Dict[str, WorkflowTypeVersion]
    supported_wes_versions: List[str] = []
    supported_filesystem_protocols: List[str] = []
    workflow_engine_versions: Dict[str, str]
    default_workflow_engine_parameters: List[DefaultWorkflowEngineParameter] = []
    auth_instructions_url: str
    tags: Dict[str, str]


class ServiceInfoBase(ServiceInfoWesBase, Service):
    """Based model for service info."""


class ServiceInfo(ServiceInfoBase):
    """Full model for service info.

    Args:
        system_state_counts: State counts for workflow runs available on this
            service.

    Attributes:
        system_state_counts: State counts for workflow runs available on this
            service.
    """

    system_state_counts: Dict[str, int]
