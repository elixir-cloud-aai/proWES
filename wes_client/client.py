"""Wes client methods implementation."""

from typing import Optional

import socket
import requests
from urllib3 import exceptions


class WesClient():
    """Client to communicate with GA4GH WES Api.

    Arguments:
        url: where the wes api is hosted on, e.g., "https://wes.rahtiapp.fi"

        base_path: Override default path at which the WES API is accessible at
                   the given WES instance. e.g., "/ga4gh/wes/v1"

        token: Bearer token to send along with WES API requests. Set if
               required by WES implementation. Alternatively, specify in API
               endpoint access methods.

    Attributes:
        url: URL to WES endpoints, built from `url` and `base_path`,
            e.g.,"https://wes.rahtiapp.fi/ga4gh/wes/v1".
        token: Bearer token for gaining access to WES endpoints.
    """
    def __init__(
        self,
        url: str,
        base_path: str = "/ga4gh/wes/v1",
        token: Optional[str] = None,
    ) -> None:
        """Class Constructor"""
        self.headers = {"Accept": "application/json"}
        self.url = url
        self.base_path = base_path
        self.session = requests.Session()
        self.session.headers.update(self.headers)
        self.token = token

    def get_runs(
        self,
        token: Optional[str] = None
    ):
        """Retrives or List runs i.e. (run_id and state) of every workflow.
        To monitor a specific workflow run, use get_run_id_status.

        Arguments:
            token: Bearer token for authentication. Set if required by WES
            implementation and if not provided when instatiating client.

        Returns:
            List runs of workflows their run_id and state in JSON response.

        Raises:
            requests.exceptions.ConnectionError: A connection to the provided
                WES instance could not be established.

        Example:
            Make a WES class instance first
            where passing url,base_path of wes api as argument
            example url = 'https://wes.rahtiapp.fi',
                    base_path = '/ga4gh/wes/v1'
            client = WesClient(url,base_path)

            Then to List runs you can call this (get_runs) method
            client.get_runs()
        """
        # get request headers
        self._get_headers(
            content_type='application/json',
            token=token,
        )
        # build request URL
        url = f"{self.url}{self.base_path}/runs"
        # send request
        try:
            response = self.session.get(url)
        except (
            requests.exceptions.ConnectionError,
            socket.gaierror,
            exceptions.NewConnectionError,
        ) as exc:
            raise requests.exceptions.ConnectionError(
                "Could not connect to API endpoint."
            ) from exc
        return response.json()

    def get_runs_id(
        self,
        run_id: str,
        token: Optional[str] = None
    ):
        """Retrives information about a given workflow run.

        Arguments:
           run_id: run_id of the workflow of which detailed information is
                   required.

           token: Bearer token for authentication. Set if required
            by WES implementation and if not provided when instatiating client.

        Returns:
            Result has information about the outputs produced by this workflow
            (if available),a log object which allows the stderr and stdout to
            be retrieved,  a log array so stderr/stdout for individual tasks
            can be retrieved, and the overall state of the workflow run.
        Raises:
            requests.exceptions.ConnectionError: A connection to the provided
                WES instance could not be established.

        Example:
            Make a WES class instance first
            where passing url,base_path of wes api as argument
            example url = 'https://wes.rahtiapp.fi',
                    base_path = '/ga4gh/wes/v1'
            client = WesClient(url,base_path)

            Then to retrive information about a given workflow run.
            where run_id is needed to be passed as an ardument
            e.g. here (run_id = "N5H4TT")
            client.get_runs_id("N5H4TT")
        """
        # get request headers
        self._get_headers(
            content_type='application/json',
            token=token,
        )
        # build request URL
        url = f"{self.url}{self.base_path}/runs/{run_id}"
        # send request
        try:
            response = self.session.get(url)
        except (
            requests.exceptions.ConnectionError,
            socket.gaierror,
            exceptions.NewConnectionError,
        ) as exc:
            raise requests.exceptions.ConnectionError(
                "Could not connect to API endpoint."
            ) from exc
        return response.json()

    def get_service_info(
        self,
        token: Optional[str] = None
    ):
        """Retrives information related the workflow descriptor formats.

        Arguments:
            token: Bearer token for authentication. Set if required
            by WES implementation and if not provided when instatiating client.

        Returns:
            Returns information related the workflow descriptor formats,
            versions supported, the WES API versions supported, and information
            about general service availability.

        Raises:
            requests.exceptions.ConnectionError: A connection to the provided
                WES instance could not be established.

        Example:
            Make a WES class instance first
            where passing url,base_path of wes api as argument
            example url = 'https://wes.rahtiapp.fi',
                    base_path = '/ga4gh/wes/v1'
            client = WesClient(url,base_path)

            Then call to get information related to workflow descriptor formats
            client.get_service_info()
        """
        # get request headers
        self._get_headers(
            content_type='application/json',
            token=token,
        )
        # build request URL
        url = f"{self.url}{self.base_path}/service-info"
        # send request
        try:
            response = self.session.get(url)
        except (
            requests.exceptions.ConnectionError,
            socket.gaierror,
            exceptions.NewConnectionError,
        ) as exc:
            raise requests.exceptions.ConnectionError(
                "Could not connect to API endpoint."
            ) from exc
        return response.json()

    def get_run_id_status(
        self,
        run_id: str,
        token: Optional[str] = None
    ):
        """This method provides an abbreviated (and likely fast depending on
        implementation) status of the running workflow, returning a simple
        result with the overall state of the workflow run.

        Arguments:
            run_id: run_id of the workflow of which information is
                   required.
            token: Bearer token for authentication. Set if required by WES
                   implementation and if not provided when instatiating client.

        Returns:
            status of the running workflow, returning a simple result with the
            overall state of the workflow run.

        Raises:
            requests.exceptions.ConnectionError: A connection to the provided
                WES instance could not be established.

        Example:
            Make a WES class instance first
            where passing url,base_path of wes api as argument
            e.g, url = 'https://wes.rahtiapp.fi',
                    base_path = '/ga4gh/wes/v1'
            client = WesClient(url,base_path)

            Then simply call this method using by passing run_id as argument.
            here,(run_id = "N5H4TT")
            client.get_run_id_status("N5H4TT")
        """
        # get request headers
        self._get_headers(
            content_type='application/json',
            token=token,
        )
        # build request URL
        url = f"{self.url}{self.base_path}/runs/{run_id}/status"
        # send request
        try:
            response = self.session.get(url)
        except (
            requests.exceptions.ConnectionError,
            socket.gaierror,
            exceptions.NewConnectionError,
        ) as exc:
            raise requests.exceptions.ConnectionError(
                "Could not connect to API endpoint."
            ) from exc
        return response.json()

    def post_workflow(
        self,
        input_data,
        token: Optional[str] = None,
    ):
        """This method creates a new workflow run and returns a RunId to
        monitor its progress.

        Arguments:
        input_data: Request body schema should of type
           workflow_params: string
           workflow_type: string
           workflow_type_version: string
           tags: string
           workflow_engine_parameters: string
           workflow_url: string
           workflow_attachment: string

        token:(Optional) Bearer token for authentication. Set if required
            by WES implementation and if not provided when instatiating client.


        Returns: returns a workflow RunId to monitor its progress.

        Raises:
            requests.exceptions.ConnectionError: A connection to the provided
                WES instance could not be established.
        """
        # get request headers
        self._get_headers(
            content_type='application/json',
            token=token,
        )
        # build request URL
        url = f"{self.url}{self.base_path}/runs"
        # send request
        try:
            response = self.session.post(url, json=input_data)
        except (
            requests.exceptions.ConnectionError,
            socket.gaierror,
            exceptions.NewConnectionError,
        ) as exc:
            raise requests.exceptions.ConnectionError(
                "Could not connect to API endpoint."
            ) from exc
        return response.json()

    def _get_headers(
        self,
        content_accept: str = 'application/json',
        content_type: Optional[str] = None,
        token: Optional[str] = None,
    ) -> None:
        """Build dictionary of request headers.

        Arguments:
            content_accept: Requested MIME/content type.

            content_type: Type of content sent with the request.

            token: Bearer token for authentication. Set if required by WES
            implementation and if not provided when instatiating client or
                if expired.
        """
        self.headers['Accept'] = content_accept
        if content_type:
            self.headers['Content-Type'] = content_type
        if token is not None:
            self.token = token
            self.headers['Authorization'] = f"Bearer {self.token}"
