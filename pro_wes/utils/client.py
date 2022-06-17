"""Basic WES client."""

import requests
import socket
from typing import (
    Dict,
    List,
    Optional,
)
from urllib3 import exceptions


class WesClient():
    """Client to communicate with GA4GH WES API.

    Arguments:
        url: URL at which the WES API is hosted, but _not_ containing the base
            path defined in the WES API specification; e.g.,
            https://my.wes.com/api, if the actual API is hosted at
            https://my.wes.com/api/ga4gh/wes/v1.
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
        url: str,
        base_path: str = "/ga4gh/wes/v1",
        token: Optional[str] = None,
    ) -> None:
        """Class Constructor"""
        self.url = f"{url}{base_path}"
        self.set_token(token)
        self.session = requests.Session()

    def get_service_info(self) -> Dict[str, str]:
        """Retrieve information about the WES instance.

        Returns:
            List of workflow runs according to WES API schema `ServiceInfo`.
            Cf.
            https://github.com/ga4gh/workflow-execution-service-schemas/blob/c5406f1d3740e21b93d3ac71a4c8d7b874011519/openapi/workflow_execution_service.swagger.yaml#L373-L441

        Raises:
            requests.exceptions.ConnectionError: A connection to the WES
                instance could not be established.
        """

        self.set_headers()
        url = f"{self.url}/service-info"

        try:
            response = self.session.get(url)
        except (
            requests.exceptions.ConnectionError,
            socket.gaierror,
            exceptions.NewConnectionError,
        ) as exc:
            raise requests.exceptions.ConnectionError(
                f"Could not connect to API endpoint at: {url}."
            ) from exc
        return response.json()

    def post_run(
        self,
        form_data: Dict[str, str],
        files: Optional[Dict] = None,
    ) -> Dict[str, str]:
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

        Returns: Workflow run identifier.

        Raises:
            requests.exceptions.ConnectionError: A connection to the WES
                instance could not be established.
        """
        self.set_headers()
        url = f"{self.url}/runs"
        if files is None:
            files = {}

        try:
            response = self.session.post(url, json=form_data, files=files)
        except (
            requests.exceptions.ConnectionError,
            socket.gaierror,
            exceptions.NewConnectionError,
        ) as exc:
            raise requests.exceptions.ConnectionError(
                f"Could not connect to API endpoint at: {url}."
            ) from exc

        return response.json()

    def get_runs(self) -> List[Dict[str, str]]:
        """Retrieve list of workflow runs.

        Returns:
            List of workflow runs according to WES API schema
            `RunListResponse`. Cf.
            https://github.com/ga4gh/workflow-execution-service-schemas/blob/c5406f1d3740e21b93d3ac71a4c8d7b874011519/openapi/workflow_execution_service.swagger.yaml#L495-L510

        Raises:
            requests.exceptions.ConnectionError: A connection to the WES
                instance could not be established.
        """

        self.set_headers()
        url = f"{self.url}/runs"

        try:
            response = self.session.get(url)
        except (
            requests.exceptions.ConnectionError,
            socket.gaierror,
            exceptions.NewConnectionError,
        ) as exc:
            raise requests.exceptions.ConnectionError(
                f"Could not connect to API endpoint at: {url}."
            ) from exc

        return response.json()

    def get_run(
        self,
        run_id: str,
    ) -> Dict[str, str]:
        """Retrieve detailed information about a workflow run.

        Args:
            run_id: Workflow run identifier.

        Returns:
            List of workflow runs according to WES API schema `RunLog`. Cf.
            https://github.com/ga4gh/workflow-execution-service-schemas/blob/c5406f1d3740e21b93d3ac71a4c8d7b874011519/openapi/workflow_execution_service.swagger.yaml#L511-L533

        Raises:
            requests.exceptions.ConnectionError: A connection to the WES
                instance could not be established.
        """

        self.set_headers()
        url = f"{self.url}/runs/{run_id}"

        try:
            response = self.session.get(url)
        except (
            requests.exceptions.ConnectionError,
            socket.gaierror,
            exceptions.NewConnectionError,
        ) as exc:
            raise requests.exceptions.ConnectionError(
                f"Could not connect to API endpoint at: {url}."
            ) from exc

        return response.json()

    def get_run_status(
        self,
        run_id: str,
    ) -> Dict[str, str]:
        """Retrieve status information about a workflow run.

        Args:
            run_id: Workflow run identifier.

        Returns:
            List of workflow runs according to WES API schema `RunStatus`. Cf.
            https://github.com/ga4gh/workflow-execution-service-schemas/blob/c5406f1d3740e21b93d3ac71a4c8d7b874011519/openapi/workflow_execution_service.swagger.yaml#L585-L594

        Raises:
            requests.exceptions.ConnectionError: A connection to the WES
                instance could not be established.
        """
        self.set_headers()
        url = f"{self.url}/runs/{run_id}/status"

        try:
            response = self.session.get(url)
        except (
            requests.exceptions.ConnectionError,
            socket.gaierror,
            exceptions.NewConnectionError,
        ) as exc:
            raise requests.exceptions.ConnectionError(
                f"Could not connect to API endpoint at: {url}."
            ) from exc

        return response.json()

    def cancel_run(
        self,
        run_id: str,
    ) -> Dict[str, str]:
        """Cancel workflow run.

        Args:
            run_id: Workflow run identifier.

        Returns: Workflow run identifier.

        Raises:
            requests.exceptions.ConnectionError: A connection to the WES
                instance could not be established.
        """
        self.set_headers()
        url = f"{self.url}/runs/{run_id}/cancel"

        try:
            response = self.session.post(url)
        except (
            requests.exceptions.ConnectionError,
            socket.gaierror,
            exceptions.NewConnectionError,
        ) as exc:
            raise requests.exceptions.ConnectionError(
                f"Could not connect to API endpoint at: {url}."
            ) from exc

        return response.json()

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
        content_accept: str = 'application/json',
        content_type: Optional[str] = None,
    ) -> None:
        """Set session headers.

        Args:
            content_accept: Requested MIME/content type.
            content_type: Type of content sent with the request.
        """
        headers = {}
        headers['Accept'] = content_accept
        if content_type is not None:
            headers['Content-Type'] = content_type
        headers['Authorization'] = f"Bearer {self.token}"
        self.session.headers.update(headers)
