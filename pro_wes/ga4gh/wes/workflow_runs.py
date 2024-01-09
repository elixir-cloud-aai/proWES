"""Controllers for the `/runs` and children routes."""

import logging
from pathlib import Path
import string  # noqa: F401 pylint: disable=unused-import
from shutil import copyfileobj
from typing import Dict, List, Optional, Mapping

from bson.objectid import ObjectId
from celery import uuid
from foca.models.config import Config
from foca.utils.misc import generate_id
from flask import current_app, request
from pymongo.collection import Collection
from pymongo.errors import DuplicateKeyError
from werkzeug.datastructures import ImmutableMultiDict
from werkzeug.utils import secure_filename

from pro_wes.ga4gh.wes.client_wes import WesClient
from pro_wes.exceptions import (
    BadRequest,
    EngineUnavailable,
    Forbidden,
    InternalServerError,
    IdsUnavailableProblem,
    RunNotFound,
    StorageUnavailableProblem,
    Unauthorized,
)
from pro_wes.ga4gh.wes.models import (
    Attachment,
    DbDocument,
    ErrorResponse,
    RunRequest,
    State,
    WesEndpoint,
)
from pro_wes.tasks.track_run_progress import task__track_run_progress
from pro_wes.utils.db import DbDocumentConnector

logger = logging.getLogger(__name__)


class WorkflowRuns:
    """Class for WES API server-side controller methods.

    Attributes:
        config: App configuration.
        foca_config: FOCA configuration.
        db_client: Database collection storing workflow run objects.
        document: Document to be inserted into the collection. Note that this is
            iteratively built up.
    """

    def __init__(self) -> None:
        """Class constructor."""
        self.config: Dict = current_app.config
        self.foca_config: Config = current_app.config["foca"]
        self.db_client: Collection = (
            self.foca_config.db.dbs["runStore"].collections["runs"].client
        )

    def run_workflow(
        self,
        **kwargs,
    ) -> Dict[str, str]:
        """Start workflow run.

        Controller for `POST /runs`.

        Args:
            **kwargs: Additional keyword arguments passed along with request.

        Returns:
            Workflow run identifier.
        """
        document: DbDocument = DbDocument()
        controller_config = self.foca_config.custom.post_runs

        # validate and attach request
        document.run_log.request = self._validate_run_request(
            form_data=request.form,
        )

        # get and attach suitable WES endpoint
        document.wes_endpoint = WesEndpoint(
            host="https://csc-wes-noauth.rahtiapp.fi",
        )

        # get and attach workflow run owner
        document.user_id = kwargs.get("user_id", None)

        # create run environment & insert run document into run collection
        document_stored = self._create_run_environment(document=document)

        # write workflow attachments
        self._save_attachments(attachments=document_stored.attachments)

        if document_stored.wes_endpoint is None:
            raise KeyError("wes endpoint is None")

        if document_stored.wes_endpoint.base_path is None:
            raise KeyError("base_path in wes endpoint is None")

        # instantiate WES client
        wes_client: WesClient = WesClient(
            host=document_stored.wes_endpoint.host,
            base_path=document_stored.wes_endpoint.base_path,
            token=kwargs.get("jwt", None),
        )

        if document_stored.task_id is None:
            raise KeyError("task_id is None")

        # instantiate database connector
        db_connector = DbDocumentConnector(
            collection=self.db_client,
            task_id=document_stored.task_id,
        )

        # forward incoming WES request and validate response
        url = (
            f"{document_stored.wes_endpoint.host.rstrip('/')}/"
            f"{document_stored.wes_endpoint.base_path.strip('/')}"
        )
        logger.info(
            f"Sending workflow run '{document_stored.run_log.run_id}' with "
            f"task identifier '{document_stored.task_id}' to WES endpoint "
            f"hosted at: {url}"
        )
        try:
            response = wes_client.post_run(
                form_data=document.run_log.request.dict(),
                timeout=controller_config.timeout_post,
            )
        except EngineUnavailable:
            db_connector.update_run_state(state=State.SYSTEM_ERROR.value)
            raise
        if isinstance(response, ErrorResponse):
            db_connector.update_run_state(state=State.SYSTEM_ERROR.value)
            if response.status_code == 400:
                raise BadRequest
            if response.status_code == 401:
                raise Unauthorized
            if response.status_code == 403:
                raise Forbidden
            raise InternalServerError

        stored_document: DbDocument | None | Mapping = (
            db_connector.upsert_fields_in_root_object(
                root="wes_endpoint",
                run_id=response.run_id,
            )
        )

        if stored_document is None or not isinstance(stored_document, DbDocument):
            raise TypeError("Unexpected type or None returned from db_connector.")

        if stored_document.wes_endpoint is None:
            raise TypeError("wes_endpoint is None")

        # track workflow progress in background
        task__track_run_progress.apply_async(
            None,
            {
                "jwt": kwargs.get("jwt", None),
                "remote_host": stored_document.wes_endpoint.host,
                "remote_base_path": stored_document.wes_endpoint.base_path,
                "remote_run_id": stored_document.wes_endpoint.run_id,
            },
            task_id=stored_document.task_id,
            soft_time_limit=controller_config.timeout_job,
        )

        if stored_document.run_log.run_id is None:
            raise TypeError("No run found")

        return {"run_id": stored_document.run_log.run_id}

    def list_runs(
        self,
        **kwargs,
    ) -> Dict:
        """Return list of workflow runs.

        Controller for `GET /runs`.

        Args:
            **kwargs: Keyword arguments passed along with request.

        Returns:
            Response object according to WES API schema `RunListResponse`. Cf.
                https://github.com/ga4gh/workflow-execution-service-schemas/blob/c5406f1d3740e21b93d3ac71a4c8d7b874011519/openapi/workflow_execution_service.swagger.yaml#L495-L510
        """
        # set query params
        page_size = kwargs.get(
            "page_size", self.foca_config.custom.list_runs.default_page_size
        )
        page_token = kwargs.get("page_token", "")

        # set filters
        filter_dict = {}
        if "user_id" in kwargs:
            filter_dict["user_id"] = kwargs["user_id"]
        if page_token != "":
            filter_dict["_id"] = {"$lt": ObjectId(page_token)}

        # get resources
        resources = list(
            self.db_client.find(
                filter=filter_dict,
                projection={
                    "run_log.run_id": True,
                    "run_log.state": True,
                },
            )
            .sort("_id", -1)
            .limit(page_size)
        )

        # set next page token
        if resources:
            next_page_token = str(resources[-1]["_id"])
        else:
            next_page_token = ""

        # format response
        for run in resources:
            run["run_id"] = run["run_log"]["run_id"]
            run["state"] = run["run_log"]["state"]
            del run["run_log"]
            del run["_id"]

        return {"next_page_token": next_page_token, "runs": resources}

    def get_run_log(
        self,
        run_id: str,
        **kwargs,
    ) -> Dict:
        """Return detailed information about a workflow run.

        Controller for `GET /runs/{run_id}`.

        Args:
            run_id: Workflow run identifier.
            **kwargs: Additional keyword arguments passed along with request.

        Returns:
            Response object according to WES API schema `RunLog`. Cf.
                https://github.com/ga4gh/workflow-execution-service-schemas/blob/c5406f1d3740e21b93d3ac71a4c8d7b874011519/openapi/workflow_execution_service.swagger.yaml#L511-L533

        Raises:
            pro_wes.exceptions.Forbidden: The requester is not allowed to access the
                resource.
            pro_wes.exceptions.RunNotFound: The requested workflow run is not available.
        """
        # retrieve workflow run
        document = self.db_client.find_one(
            filter={"run_log.run_id": run_id},
            projection={
                "user_id": True,
                "run_log": True,
                "_id": False,
            },
        )

        # raise error if workflow run was not found
        if document is None:
            logger.error(f"Run '{run_id}' not found.")
            raise RunNotFound

        # raise error trying to access workflow run that is not owned by user
        # only if authorization enabled
        self._check_access_permission(
            resource_id=run_id,
            owner=document.get("user_id", None),
            requester=kwargs.get("user_id", None),
        )

        return document["run_log"]

    def get_run_status(
        self,
        run_id: str,
        **kwargs,
    ) -> Dict:
        """Return status information about a workflow run.

        Controller for `GET /runs/{run_id}/status`.

        Args:
            run_id: Workflow run identifier.
            **kwargs: Additional keyword arguments passed along with request.

        Returns:
            Response object according to WES API schema `RunStatus`. Cf.
                https://github.com/ga4gh/workflow-execution-service-schemas/blob/c5406f1d3740e21b93d3ac71a4c8d7b874011519/openapi/workflow_execution_service.swagger.yaml#L585-L594

        Raises:
            pro_wes.exceptions.Forbidden: The requester is not allowed to access the
                resource.
            pro_wes.exceptions.RunNotFound: The requested workflow run is not available.
        """
        # retrieve workflow run
        document = self.db_client.find_one(
            filter={"run_log.run_id": run_id},
            projection={
                "user_id": True,
                "run_log.state": True,
                "_id": False,
            },
        )

        # ensure resource is available
        if document is None:
            logger.error(f"Run '{run_id}' not found.")
            raise RunNotFound

        # ensure requester has access
        self._check_access_permission(
            resource_id=run_id,
            owner=document.get("user_id", None),
            requester=kwargs.get("user_id", None),
        )

        return {
            "run_id": run_id,
            "state": document["run_log"]["state"],
        }

    def cancel_run(
        self,
        run_id: str,
        **kwargs,
    ) -> Dict[str, str]:
        """Cancel workflow run.

        Controller for `GET /runs/{run_id}/cancel`.

        Args:
            run_id: Workflow run identifier.
            **kwargs: Additional keyword arguments passed along with request.

        Returns:
            Workflow run identifier.

        Raises:
            pro_wes.exceptions.Forbidden: The requester is not allowed to access the
                resource.
            pro_wes.exceptions.RunNotFound: The requested workflow run is not available.
        """
        # retrieve workflow run
        document = self.db_client.find_one(
            filter={"run_log.run_id": run_id},
            projection={
                "user_id": True,
                "wes_endpoint.host": True,
                "wes_endpoint.base_path": True,
                "wes_endpoint.run_id": True,
                "_id": False,
            },
        )

        # ensure resource is available
        if document is None:
            logger.error(f"Run '{run_id}' not found.")
            raise RunNotFound

        # ensure requester has access
        self._check_access_permission(
            resource_id=run_id,
            owner=document.get("user_id", None),
            requester=kwargs.get("user_id", None),
        )

        # cancel workflow run
        wes_client: WesClient = WesClient(
            host=document["wes_endpoint"]["host"],
            base_path=document["wes_endpoint"]["base_path"],
            token=kwargs.get("jwt", None),
        )
        wes_client.cancel_run(run_id=document["wes_endpoint"]["run_id"])

        return {"run_id": run_id}

    def _create_run_environment(
        self,
        document: DbDocument,
    ) -> DbDocument:
        """Set up run environment.

        Create unique run identifier and permanent and temporary storage directories for
        current run.

        Args:
            document: Document to be inserted into the run collection.

        Returns:
            document: Updated documented as was inserted into the database.

        Raises:
            pro_wes.exceptions.StorageUnavailableProblem: Raised if configured storage
                location is unavailable for writing.
            pro_wes.exceptions.IdsUnavailableProblem: Raised if no unique run identifier
                could be found.
        """
        controller_config = self.foca_config.custom.post_runs
        # try until unused run id was found
        attempt = 1
        while attempt <= controller_config.db_insert_attempts:
            attempt += 1
            run_id = generate_id(
                charset=controller_config.id_charset,
                length=controller_config.id_length,
            )
            work_dir = Path(controller_config.storage_path).resolve() / run_id

            # try to create working directory
            try:
                work_dir.mkdir(parents=False, exist_ok=False)
            except FileExistsError:
                continue
            except FileNotFoundError as exc:
                raise StorageUnavailableProblem from exc

            # populate document
            document.run_log.run_id = run_id
            document.task_id = uuid()
            document.work_dir = work_dir.as_posix()
            document.attachments = self._process_attachments(
                work_dir=work_dir,
            )

            # insert document into database
            try:
                self.db_client.insert(
                    document.dict(
                        exclude_none=True,
                    )
                )
            except DuplicateKeyError:
                work_dir.rmdir()
                continue
            return document

        raise IdsUnavailableProblem

    def _process_attachments(self, work_dir: Path) -> List[Attachment]:
        """Return list of file attachments from request.

        Args:
            work_dir: Working directory for constructing filenames for later storage.

        Returns:
            List of `Attachment` model instances.
        """
        attachments = []
        files = request.files.getlist("workflow_attachment")
        for file in files:
            if file.filename is not None:
                attachments.append(
                    Attachment(
                        filename=file.filename,
                        object=file.stream.read(),
                        path=work_dir
                        / self._secure_filename(
                            name=Path(file.filename),
                        ),
                    )
                )
        return attachments

    @staticmethod
    def _validate_run_request(
        form_data: ImmutableMultiDict,
    ) -> RunRequest:
        """Convert run request form input to `RunRequest` model.

        Args:
            form_data: Flask data structure for representing form values.
        """
        dict_of_lists = form_data.to_dict(flat=False)
        # flatten single item lists
        dict_atomic = {k: v[0] if len(v) == 1 else v for k, v in dict_of_lists.items()}
        # remove 'workflow_attachment' field
        dict_atomic.pop("workflow_attachment", None)
        model_instance = RunRequest(**dict_atomic)
        return model_instance

    @staticmethod
    def _secure_filename(name: Path) -> Path:
        """Return a secure version of a filename.

        Args:
            filename: Potentially insecure filename.

        Returns:
            Secure filename.
        """
        name_secure = secure_filename(str(name))
        if not name_secure:
            name_secure = uuid()
        return Path(name_secure)

    @staticmethod
    def _save_attachments(attachments: List[Attachment]) -> None:
        """Write workflow attachments to storage.

        Args:
            attachments: List of `Attachment` model instances.
        """
        files = request.files.getlist("workflow_attachment")
        for attachment in attachments:
            with open(attachment.path, "wb") as dest:
                for file in files:
                    if file.filename == attachment.filename:
                        copyfileobj(file.stream, dest)

    @staticmethod
    def _check_access_permission(
        resource_id: str,
        owner: Optional[str] = None,
        requester: Optional[str] = None,
    ) -> None:
        """Check whether requester has access to resource.

        Raise `403/Forbidden` response if resource owner is known and requester is not
        owner.

        Args:
            resource_id: Workflow run identifier.
            owner: Identifier of resource owner.
            requester: Unique, persistent identifier of resource requester.

        Raises:
            pro_wes.exceptions.Forbidden: The requester is not allowed to access the
                resource.
        """
        if requester is not None and requester != owner:
            logger.error(
                (
                    f"User '{requester}' is not allowed to access workflow run "
                    f"'{resource_id}'."
                )
            )
            raise Forbidden
