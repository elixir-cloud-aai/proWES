"""proWES schema models."""

from enum import (
    Enum,
)
from json import (
    loads,
    JSONDecodeError,
)
from pathlib import Path
from typing import (
    Dict,
    List,
    Optional,
)

from pydantic import (
    BaseModel,
    root_validator,
    validator,
)

from pro_wes.exceptions import NoSuitableEngine
from pro_wes.ga4gh.wes.service_info import ServiceInfo


class Attachment(BaseModel):
    """Model for workflow attachment.

    Args:
        filename: Name of the file as indicated in the run request.
        path: Path to the file on the app's storage system.
    """
    filename: str
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
    tags: Optional[str] = '{}'
    workflow_engine_parameters: Optional[str] = '{}'
    workflow_url: str

    @validator(
        'workflow_type',
        'workflow_type_version',
        'workflow_url',
        always=True,
    )
    def required_str_field_not_empty(
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
        if value == '' or value is None:
            raise ValueError("field required")
        return value

    @validator(
        'workflow_params',
        'tags',
        'workflow_engine_parameters',
        always=True,
    )
    def json_serialized_object_field_valid(
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
        if value == '' or value == 'null' or value is None:
            if field.name == 'workflow_params':
                raise ValueError("field required")
            return '{}'
        try:
            decoded = loads(value)
        except JSONDecodeError:
            raise ValueError("could not be JSON deserialized")
        if not isinstance(decoded, dict):
            raise ValueError("could not be interpreted as object")
        return value

    @root_validator
    def workflow_type_and_version_supported(
        cls,
        values: Dict,
    ) -> str:
        """Ensure that workflow type and version are supported by this service
        instance.

        Args:
            values (Dict): Field values dictionary.

        Returns:
            The validated field values.

        Raises:
            NoSuitableEngine: The service does not know of a suitable workflow
                engine service to process this request.
        """
        service_info = ServiceInfo().get_service_info(get_counts=False)
        type_versions = service_info['workflow_type_versions']
        type = values.get('workflow_type')
        version = values.get('workflow_type_version')
        if (
            type not in type_versions or
            version not in type_versions[type]['workflow_type_version']
        ):
            raise NoSuitableEngine
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
    cmd: Optional[List[str]]
    end_time: Optional[str]
    exit_code: Optional[int]
    name: Optional[str]
    start_time: Optional[str]
    stderr: Optional[str]
    stdout: Optional[str]


class State(Enum):
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
    UNKNOWN = 'UNKNOWN'
    QUEUED = 'QUEUED'
    INITIALIZING = 'INITIALIZING'
    RUNNING = 'RUNNING'
    PAUSED = 'PAUSED'
    COMPLETE = 'COMPLETE'
    EXECUTOR_ERROR = 'EXECUTOR_ERROR'
    SYSTEM_ERROR = 'SYSTEM_ERROR'
    CANCELED = 'CANCELED'
    CANCELING = 'CANCELING'


class RunLog(BaseModel):
    """Model for entire workflow run log.

    Args:
        outputs: Name and destination of workflow outputs.
        run_request: Form data passed during original workflow run request.
        run_id: Unique identifier of workflow run.
        run_log: Log of workflow engine itself.
        state: State of workflow run.
        task_logs: List of workflow task/job logs.

    Attributes:
        outputs: Name and destination of workflow outputs.
        run_request: Form data passed during original workflow run request.
        run_id: Unique identifier of workflow run.
        run_log: Log of workflow engine itself.
        state: State of workflow run.
        task_logs: List of workflow task/job logs.
    """
    outputs: Optional[Dict[str, str]]
    run_request: Optional[RunRequest]
    run_id: Optional[str]
    run_log: Optional[Log]
    state: State = State.UNKNOWN
    task_logs: Optional[List[Log]]

    class Config:
        use_enum_values = True


class WesEndpoint(BaseModel):
    """Model for information on the WES endpoint to which the incoming
    workflow run request was relayed.

    Args:
        url: Base URL at which the WES endpoint is deployed.
        base_path: Base path; only required if the WES API is deployed at a
            non-standard route.

    Attributes:
        url: Base URL at which the WES endpoint is deployed.
        base_path: Base path; only required if the WES API is deployed at a
            non-standard route.
    """
    url: str
    base_path: Optional[str] = '/ga4gh/wes/v1'


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
    task_id: Optional[str]
    user_id: Optional[str]
    work_dir: Optional[Path]
    wes_endpoint: Optional[WesEndpoint]
