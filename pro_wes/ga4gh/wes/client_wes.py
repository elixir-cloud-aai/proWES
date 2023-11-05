"""Basic WES client."""

from typing import Dict, Optional, Union

from pydantic import ValidationError
import requests
from requests.exceptions import RequestException

from pro_wes.exceptions import EngineUnavailable
from pro_wes.ga4gh.wes.models import (
    ErrorResponse,
    RunRequest,
    RunListResponse,
    RunStatus,
    RunId,
    RunLog,
    ServiceInfo,
)


class WesClient:
    """Client to communicate with GA4GH WES API.

    Arguments:
        host: Host at which the WES API is served; note that this should
            include the path information but *not* the base path path defined
            in the WES API specification; e.g., specify https://my.wes.com/api
            if the actual API is hosted at https://my.wes.com/api/ga4gh/wes/v1.
        base_path: Override the default path suffix defined in the WES API
            specification.
        token: Bearer token to send along with any WES API requests. Set if
            required by WES instance. Alternatively, use `set_token()` method
            to set.

    Attributes:
        url: URL to WES endpoints, built from `url` and `base_path`,
            e.g.,"https://wes.rahtiapp.fi/ga4gh/wes/v1".
        token: Bearer token for gaining access to WES endpoints.
        session: Client server session.
    """

    def __init__(
        self,
        host: str,
        base_path: str = "/ga4gh/wes/v1",
        token: Optional[str] = None,
    ) -> None:
        """Class Constructor"""
        self.url = f"{host.rstrip('/')}/{base_path.strip('/')}"
        self.set_token(token)
        self.session = requests.Session()

    def get_service_info(
        self,
        **kwargs,
    ) -> Union[ErrorResponse, ServiceInfo]:
        """Retrieve information about the WES instance.

        Args:
            **kwargs: Additional keyword arguments passed along with request.

        Returns:
            Response object according to WES API schema `ServiceInfo`. Cf.
                https://github.com/ga4gh/workflow-execution-service-schemas/blob/c5406f1d3740e21b93d3ac71a4c8d7b874011519/openapi/workflow_execution_service.swagger.yaml#L373-L441
        """
        self.set_headers()
        url = f"{self.url}/service-info"
        response: Union[ErrorResponse, ServiceInfo]
        try:
            response_unvalidated = self.session.get(url, **kwargs).json()
        except (RequestException, ValueError) as exc:
            raise EngineUnavailable("external workflow engine unavailable") from exc
        try:
            response = ServiceInfo(**response_unvalidated)
        except ValidationError:
            try:
                response = ErrorResponse(**response_unvalidated)
            except ValidationError as exc:
                raise ValueError(f"invalid response: {response_unvalidated}") from exc
        return response

    def post_run(
        self,
        form_data: Dict[str, str],
        files: Optional[Dict] = None,
        **kwargs,
    ) -> Union[ErrorResponse, RunId]:
        """Send workflow run request.

        Args:
            form_data: Form data according to WES API schema `RunRequest`. Cf.
                https://github.com/ga4gh/workflow-execution-service-schemas/blob/c5406f1d3740e21b93d3ac71a4c8d7b874011519/openapi/workflow_execution_service.swagger.yaml#L534-L578
                The following form fields are required:
                * `workflow_params`
                * `workflow_type`
                * `workflow_type_version`
                * `workflow_url`
                The following form fields are optional:
                * `tags`
                * `workflow_engine_parameters`
            files: Dictionary of files to be attached. Cf.
                https://requests.readthedocs.io/en/latest/api/#requests.request
                for possible structures of dictionary.
            timeout: Request timeout in seconds. Set to `None` to disable
                timeout.

        Returns:
            WES API schema `RunId`. Cf.
                https://github.com/ga4gh/workflow-execution-service-schemas/blob/c5406f1d3740e21b93d3ac71a4c8d7b874011519/openapi/workflow_execution_service.swagger.yaml#L495-L510

        Raises:
            ValueError: The form data does not conform to the expected schema.
            ValueError: The response does not conform to any of the expected
                schemas.
        """
        self.set_headers()
        url = f"{self.url}/runs"
        response: Union[ErrorResponse, RunId]
        if files is None:
            files = {}
        try:
            RunRequest(**form_data)
        except Exception as exc:
            raise ValueError(f"invalid form data: {form_data}") from exc
        try:
            response_unvalidated = self.session.post(
                url,
                data=form_data,
                files=files,
                **kwargs,
            ).json()
        except (RequestException, ValueError) as exc:
            raise EngineUnavailable("external workflow engine unavailable") from exc
        try:
            response = RunId(**response_unvalidated)
        except ValidationError:
            try:
                response = ErrorResponse(**response_unvalidated)
            except ValidationError as exc:
                raise ValueError(f"invalid response: {response_unvalidated}") from exc
        return response

    def get_runs(
        self,
        **kwargs,
    ) -> Union[ErrorResponse, RunListResponse]:
        """Retrieve list of workflow runs.

        Args:
            timeout: Request timeout in seconds. Set to `None` to disable
                timeout.

        Returns:
            WES API schema `RunListResponse`. Cf.
                https://github.com/ga4gh/workflow-execution-service-schemas/blob/c5406f1d3740e21b93d3ac71a4c8d7b874011519/openapi/workflow_execution_service.swagger.yaml#L495-L510

        Raises:
            ValueError: The response does not conform to any of the expected
                schemas.
        """

        self.set_headers()
        url = f"{self.url}/runs"
        response: Union[ErrorResponse, RunListResponse]
        try:
            response_unvalidated = self.session.get(url, **kwargs).json()
        except (RequestException, ValueError) as exc:
            raise EngineUnavailable("external workflow engine unavailable") from exc
        try:
            response = RunListResponse(**response_unvalidated)
        except ValidationError:
            try:
                response = ErrorResponse(**response_unvalidated)
            except ValidationError as exc:
                raise ValueError(f"invalid response: {response_unvalidated}") from exc
        return response

    def get_run(
        self,
        run_id: str,
        **kwargs,
    ) -> RunLog:
        """Retrieve detailed information about a workflow run.

        Args:
            run_id: Workflow run identifier.
            timeout: Request timeout in seconds. Set to `None` to disable
                timeout.

        Returns:
            WES API schema `RunLog`. Cf.
                https://github.com/ga4gh/workflow-execution-service-schemas/blob/c5406f1d3740e21b93d3ac71a4c8d7b874011519/openapi/workflow_execution_service.swagger.yaml#L511-L533

        Raises:
            ValueError: The response does not conform to any of the expected
                schemas.
        """

        self.set_headers()
        url = f"{self.url}/runs/{run_id}"
        try:
            response_unvalidated = self.session.get(url, **kwargs).json()
        except (RequestException, ValueError) as exc:
            raise EngineUnavailable("external workflow engine unavailable") from exc
        # skip validation; workaround for cwl-WES
        return response_unvalidated
        try:  # pylint: disable=unreachable
            response = RunLog(**response_unvalidated)
        except ValidationError:
            try:
                response = ErrorResponse(**response_unvalidated)
            except ValidationError as exc:
                raise ValueError(f"invalid response: {response_unvalidated}") from exc
        return response

    def get_run_status(
        self,
        run_id: str,
        **kwargs,
    ) -> Union[ErrorResponse, RunStatus]:
        """Retrieve status information about a workflow run.

        Args:
            run_id: Workflow run identifier.
            timeout: Request timeout in seconds. Set to `None` to disable
                timeout.

        Returns:
            WES API schema `RunStatus`. Cf.
                https://github.com/ga4gh/workflow-execution-service-schemas/blob/c5406f1d3740e21b93d3ac71a4c8d7b874011519/openapi/workflow_execution_service.swagger.yaml#L585-L594

        Raises:
            ValueError: The response does not conform to any of the expected
                schemas.
        """
        self.set_headers()
        url = f"{self.url}/runs/{run_id}/status"
        response: Union[ErrorResponse, RunStatus]
        try:
            response_unvalidated = self.session.get(url, **kwargs).json()
        except (RequestException, ValueError) as exc:
            raise EngineUnavailable("external workflow engine unavailable") from exc
        try:
            response = RunStatus(**response_unvalidated)
        except ValidationError:
            try:
                response = ErrorResponse(**response_unvalidated)
            except ValidationError as exc:
                raise ValueError(f"invalid response: {response_unvalidated}") from exc
        return response

    def cancel_run(
        self,
        run_id: str,
        **kwargs,
    ) -> Union[ErrorResponse, RunId]:
        """Cancel workflow run.

        Args:
            run_id: Workflow run identifier.
            timeout: Request timeout in seconds. Set to `None` to disable
                timeout.

        Returns:
            WES API schema `RunId`. Cf.
                https://github.com/ga4gh/workflow-execution-service-schemas/blob/c5406f1d3740e21b93d3ac71a4c8d7b874011519/openapi/workflow_execution_service.swagger.yaml#L585-L594

        Raises:
            ValueError: The response does not conform to any of the expected
                schemas.
        """
        self.set_headers()
        url = f"{self.url}/runs/{run_id}/cancel"
        response: Union[ErrorResponse, RunId]
        try:
            response_unvalidated = self.session.post(url, **kwargs).json()
        except (RequestException, ValueError) as exc:
            raise EngineUnavailable("external workflow engine unavailable") from exc
        try:
            response = RunId(**response_unvalidated)
        except ValidationError:
            try:
                response = ErrorResponse(**response_unvalidated)
            except ValidationError as exc:
                raise ValueError(f"invalid response: {response_unvalidated}") from exc
        return response

    def set_token(
        self,
        token: Optional[str] = None,
    ) -> None:
        """Set access token for session.

        Args:
            token: Bearer token to send along with any WES API requests. Set if
                required by WES instance.
        """
        self.token = token

    def set_headers(
        self,
        content_accept: str = "application/json",
        content_type: Optional[str] = None,
    ) -> None:
        """Set session headers.

        Args:
            content_accept: Requested MIME/content type.
            content_type: Type of content sent with the request.
        """
        headers = {}
        headers["Accept"] = content_accept
        if content_type is not None:
            headers["Content-Type"] = content_type
        headers["Authorization"] = f"Bearer {self.token}"
        self.session.headers.update(headers)
