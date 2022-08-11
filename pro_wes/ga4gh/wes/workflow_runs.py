"""Controllers for the `/runs` and children routes."""

import logging
import string  # noqa: F401
from shutil import copyfileobj
from typing import (
    Dict,
    List,
    Optional,
)

from bson.objectid import ObjectId
from celery import uuid
from foca.models.config import Config
from foca.utils.misc import generate_id
from flask import (
    current_app,
    request,
)
from pathlib import Path
from pymongo.collection import Collection
from pymongo.errors import DuplicateKeyError
from werkzeug.datastructures import ImmutableMultiDict
from werkzeug.utils import secure_filename

from pro_wes.client_wes import WesClient
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

    def __init__(self) -> None:
        """Class for WES API server-side controller methods.

        Attributes:
            config: App configuration.
            foca_config: FOCA configuration.
            db_client: Database collection storing workflow run objects.
            document: Document to be inserted into the collection. Note that
                this is iteratively built up.
        """
        self.config: Dict = current_app.config
        self.foca_config: Config = current_app.config.foca
        self.db_client: Collection = (
            self.foca_config.db.dbs['runStore'].collections['runs'].client
        )

    # controller method for `POST /runs`
    def run_workflow(
        self,
        **kwargs,
    ) -> Dict[str, str]:
        """Start workflow run.

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
        document.user_id = kwargs.get('user_id', None)

        # create run environment & insert run document into run collection
        document_stored = self._create_run_environment(document=document)

        # write workflow attachments
        self._save_attachments(attachments=document_stored.attachments)

        # instantiate WES client
        wes_client: WesClient = WesClient(
            host=document_stored.wes_endpoint.host,
            base_path=document_stored.wes_endpoint.base_path,
            token=kwargs.get('jwt', None),
        )

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
            db_connector.update_task_state(state=State.SYSTEM_ERROR.value)
            raise
        if isinstance(response, ErrorResponse):
            db_connector.update_task_state(state=State.SYSTEM_ERROR.value)
            if response.status_code == 400:
                raise BadRequest
            elif response.status_code == 401:
                raise Unauthorized
            elif response.status_code == 403:
                raise Forbidden
            else:
                raise InternalServerError
        document_stored: DbDocument = (
            db_connector.upsert_fields_in_root_object(
                root='wes_endpoint',
                run_id=response.run_id,
            )
        )

        # track workflow progress in background
        task__track_run_progress.apply_async(
            None,
            {
                'jwt': kwargs.get('jwt', None),
                'remote_host': document_stored.wes_endpoint.host,
                'remote_base_path': document_stored.wes_endpoint.base_path,
                'remote_run_id': document_stored.wes_endpoint.run_id,
            },
            task_id=document_stored.task_id,
            soft_time_limit=controller_config.timeout_job,
        )

        return {'run_id': document_stored.run_log.run_id}

    # controller method for `GET /runs`
    def list_runs(
        self,
        **kwargs,
    ) -> Dict:
        """Return list of workflow runs.

        Args:
            **kwargs: Keyword arguments passed along with request.

        Returns:
            Response object according to WES API schema `RunListResponse`. Cf.
                https://github.com/ga4gh/workflow-execution-service-schemas/blob/c5406f1d3740e21b93d3ac71a4c8d7b874011519/openapi/workflow_execution_service.swagger.yaml#L495-L510
        """
        # fall back to default page size if not provided by user
        if 'page_size' in kwargs:
            page_size = kwargs['page_size']
        else:
            page_size = (
                self.foca_config.custom.list_runs.default_page_size
            )

        # extract/set page token
        if 'page_token' in kwargs:
            page_token = kwargs['page_token']
        else:
            page_token = ''

        # initialize filter dictionary
        filter_dict = {}

        # add filter for user-owned runs if user ID is available
        if 'user_id' in kwargs:
            filter_dict['user_id'] = kwargs['user_id']

        # add pagination filter based on last object ID
        if page_token != '':
            filter_dict['_id'] = {'$lt': ObjectId(page_token)}

        # query database for workflow runs
        cursor = self.db_client.find(
            filter=filter_dict,
            projection={
                'run_log.run_id': True,
                'run_log.state': True,
            }
            # sort results by descending object ID (+/- newest to oldest)
            ).sort(
                '_id', -1
            # implement page size limit
            ).limit(
                page_size
            )

        # convert cursor to list
        runs_list = list(cursor)

        # get next page token from ID of last run in cursor
        if runs_list:
            next_page_token = str(runs_list[-1]['_id'])
        else:
            next_page_token = ''

        # reshape list of runs
        for run in runs_list:
            run['run_id'] = run['run_log']['run_id']
            run['state'] = run['run_log']['state']
            del run['run_log']
            del run['_id']

        # build and return response
        return {
            'next_page_token': next_page_token,
            'runs': runs_list
        }

    # controller method for `GET /runs/{run_id}`
    def get_run_log(
        self,
        run_id: str,
        **kwargs,
    ) -> Dict:
        """Return detailed information about a workflow run.

        Args:
            run_id: Workflow run identifier.
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
        # retrieve workflow run
        document = self.db_client.find_one(
            filter={'run_log.run_id': run_id},
            projection={
                'user_id': True,
                'run_log': True,
                '_id': False,
            }
        )

        # raise error if workflow run was not found
        if document is None:
            logger.error("Run '{run_id}' not found.".format(run_id=run_id))
            raise RunNotFound

        # raise error trying to access workflow run that is not owned by user
        # only if authorization enabled
        self._check_access_permission(
            resource_id=run_id,
            owner=document.get('user_id', None),
            requester=kwargs.get('user_id', None),
        )

        return document['run_log']

    # controller method for `GET /runs/{run_id}/status`
    def get_run_status(
        self,
        run_id: str,
        **kwargs,
    ) -> Dict:
        """Return status information about a workflow run.

        Args:
            run_id: Workflow run identifier.
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
        # retrieve workflow run
        document = self.db_client.find_one(
            filter={'run_log.run_id': run_id},
            projection={
                'user_id': True,
                'run_log.state': True,
                '_id': False,
            }
        )

        # ensure resource is available
        if document is None:
            logger.error("Run '{run_id}' not found.".format(run_id=run_id))
            raise RunNotFound

        # ensure requester has access
        self._check_access_permission(
            resource_id=run_id,
            owner=document.get('user_id', None),
            requester=kwargs.get('user_id', None),
        )

        return {
            'run_id': run_id,
            'state': document['run_log']['state'],
        }

    # controller method for `POST /runs/{run_id}/cancel`
    def cancel_run(
        self,
        run_id: str,
        **kwargs,
    ) -> Dict[str, str]:
        """Cancel workflow run.

        Args:
            run_id: Workflow run identifier.
            **kwargs: Additional keyword arguments passed along with request.

        Returns:
            Workflow run identifier.

        Raises:
            pro_wes.exceptions.Forbidden: The requester is not allowed to
                access the resource.
            pro_wes.exceptions.RunNotFound: The requested workflow run is not
                available.
        """
        # retrieve workflow run
        document = self.db_client.find_one(
            filter={'run_log.run_id': run_id},
            projection={
                'user_id': True,
                'wes_endpoint.host': True,
                'wes_endpoint.base_path': True,
                'wes_endpoint.run_id': True,
                '_id': False,
            }
        )

        # ensure resource is available
        if document is None:
            logger.error("Run '{run_id}' not found.".format(run_id=run_id))
            raise RunNotFound

        # ensure requester has access
        self._check_access_permission(
            resource_id=run_id,
            owner=document.get('user_id', None),
            requester=kwargs.get('user_id', None),
        )

        # cancel workflow run
        wes_client: WesClient = WesClient(
            host=document['wes_endpoint']['host'],
            base_path=document['wes_endpoint']['base_path'],
            token=kwargs.get('jwt', None),
        )
        wes_client.cancel_run(run_id=document['wes_endpoint']['run_id'])

        return {'run_id': run_id}

    def _create_run_environment(
        self,
        document: DbDocument,
    ) -> DbDocument:
        """Creates unique run identifier and permanent and temporary storage
        directories for current run.

        Args:
            document: Document to be inserted into the run collection.

        Returns:
            document: Updated documented as was inserted into the database.

        Raises:
            pro_wes.exceptions.StorageUnavailableProblem: Raised if configured
                storage location is unavailable for writing.
            pro_wes.exceptions.IdsUnavailableProblem: Raised if no unique run
                identifier could be found.
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
            work_dir = Path(
                controller_config.storage_path
            ).resolve() / run_id

            # try to create working directory
            try:
                work_dir.mkdir(parents=False, exist_ok=False)
            except FileExistsError:
                continue
            except FileNotFoundError:
                raise StorageUnavailableProblem

            # populate document
            document.run_log.run_id = run_id
            document.task_id = uuid()
            document.work_dir = str(work_dir)
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
            work_dir: Working directory for constructing filenames for later
                storage.

        Returns:
            List of `Attachment` model instances.
        """
        attachments = []
        logger.warning(request.files)
        files = request.files.getlist("workflow_attachment")
        logger.warning(f"FILES: {files}")
        for file in files:
            attachments.append(
                Attachment(
                    filename=file.filename,
                    object=file.stream,
                    path=str(work_dir / self._secure_filename(
                        name=Path(file.filename),
                    ))
                )
            )
        logger.warning(f"ATTACHMENTS: {attachments}")
        return attachments

    @staticmethod
    def _validate_run_request(
        form_data: ImmutableMultiDict,
    ) -> RunRequest:
        """Convert run request form input to `RunRequest` model.

        Args:
            form_data: `werkzeug`/Flask data structure for representing form
                values.
        """
        dict_of_lists = form_data.to_dict(flat=False)
        # flatten single item lists
        dict_atomic = {
            k: v[0] if len(v) == 1 else v for
            k, v in dict_of_lists.items()
        }
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
        logger.warning(files)
        for attachment in attachments:
            with open(attachment.path, "wb") as dest:
                for file in files:
                    if file.filename == attachment.filename:
                        copyfileobj(file.stream, dest)
        return None

    @staticmethod
    def _check_access_permission(
        resource_id: str,
        owner: Optional[str] = None,
        requester: Optional[str] = None,
    ) -> None:
        """Check whether requester has access to resource.

        Raise `403/Forbidden` response if resource owner is known and requester
        is not owner.

        Args:
            resource_id: Workflow run identifier.
            owner: Identifier of resource owner.
            requester: Unique, persistent identifier of resource requester.

        Raises:
            pro_wes.exceptions.Forbidden: The requester is not allowed to
                access the resource.
        """
        if requester is not None and requester != owner:
            logger.error(
                (
                    "User '{user_id}' is not allowed to access workflow run "
                    "'{resource_id}'."
                ).format(
                    user_id=requester,
                    resource_id=resource_id,
                )
            )
            raise Forbidden
