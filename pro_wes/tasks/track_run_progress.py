"""Celery background task to start workflow run."""

import logging
from time import sleep
from typing import Dict, Optional

from foca.database.register_mongodb import _create_mongo_client
from foca.models.config import Config
from flask import Flask, current_app

from pro_wes.exceptions import EngineProblem, EngineUnavailable
from pro_wes.ga4gh.wes.models import (  # noqa: F401 pylint: disable=unused-import
    DbDocument,
    RunLog,
    RunStatus,
    State,
)
from pro_wes.utils.db import DbDocumentConnector
from pro_wes.ga4gh.wes.client_wes import WesClient
from pro_wes.celery_worker import celery
from pro_wes.exceptions import WesEndpointProblem

logger = logging.getLogger(__name__)


@celery.task(
    name="tasks.track_run_progress",
    bind=True,
    ignore_result=True,
    track_started=True,
)
def task__track_run_progress(  # pylint: disable=too-many-statements
    self,
    remote_host: str,
    remote_base_path: str,
    remote_run_id: str,
    jwt: Optional[str],
) -> str:
    """Relay workflow run request to remote WES and track run progress.

    Args:
        jwt: Authorization bearer token to be passed on with workflow run
            request to remote service.
        remote_host: Host at which the WES API is served that is processing
            this request; note that this should include the path information
            but *not* the base path path defined in the WES API specification;
            e.g., specify https://my.wes.com/api if the actual API is hosted at
            https://my.wes.com/api/ga4gh/wes/v1.
        remote_base_path: Override the default path suffix defined in the WES
            API specification, i.e., `/ga4gh/wes/v1`.
        remote_run_id: Workflow run identifier on remote WES service.

    Returns:
        Task identifier.

    Raises:
        pro_wes.exceptions.EngineUnavailable: The remote service is unavailable
            or is not a valid WES service.
    """
    foca_config: Config = current_app.config.foca
    controller_config: Dict = foca_config.custom.post_runs

    logger.info(f"[{self.request.id}] Start processing...")

    # create database client
    collection = _create_mongo_client(
        app=Flask(__name__),
        host=foca_config.db.host,
        port=foca_config.db.port,
        db="runStore",
    ).db["runs"]
    db_client = DbDocumentConnector(
        collection=collection,
        task_id=self.request.id,
    )

    # update state: INITIALIZING
    db_client.update_run_state(state=State.INITIALIZING.value)

    # instantiate WES client
    wes_client: WesClient = WesClient(
        host=remote_host,
        base_path=remote_base_path,
        token=jwt,
    )

    # fetch run log and upsert database document
    try:
        # workaround for cwl-WES; add .dict() when cwl-WES response conforms
        # to model
        response: RunLog = wes_client.get_run(run_id=remote_run_id)
    except EngineUnavailable:
        db_client.update_run_state(state=State.SYSTEM_ERROR.value)
        raise
    #    if not isinstance(response, RunLog):
    #        db_client.update_run_state(state=State.SYSTEM_ERROR.value)
    #        raise EngineProblem("Did not receive expected response.")
    response.pop("request", None)
    document: DbDocument = db_client.upsert_fields_in_root_object(
        root="run_log",
        **response.dict(),
    )

    # track workflow run progress
    run_state: State = State.UNKNOWN
    attempt: int = 1
    while not run_state.is_finished:
        sleep(controller_config.polling_wait)

        # ensure WES endpoint is available
        assert document.wes_endpoint is not None, "No WES endpoint available."
        if document.wes_endpoint.run_id is None:
            raise WesEndpointProblem
        try:
            wes_client.get_run_status(
                run_id=document.wes_endpoint.run_id,
                timeout=foca_config.custom.defaults.timeout,
            )
        except EngineUnavailable as exc:
            if attempt <= controller_config.polling_attempts:
                attempt += 1
                logger.warning(exc, exc_info=True)
                continue
            db_client.update_run_state(state=State.SYSTEM_ERROR.value)
            raise
        if not isinstance(response, RunStatus):
            if attempt <= controller_config.polling_attempts:
                attempt += 1
                logger.warning(f"Received error response: {response}")
                continue
            db_client.update_run_state(state=State.SYSTEM_ERROR.value)
            raise EngineProblem("Received too many error responses.")
        attempt = 1
        if response.state != run_state:
            run_state = response.state
            db_client.update_run_state(state=run_state.value)

    assert response.run_id is not None, "WES run ID not available."

    # fetch run log and upsert database document
    try:
        # workaround for cwl-WES; add .dict() when cwl-WES response conforms
        # to model
        response = wes_client.get_run(run_id=response.run_id)
    except EngineUnavailable:
        db_client.update_run_state(state=State.SYSTEM_ERROR.value)
        raise
    #    if not isinstance(response, RunLog):
    #        db_client.update_run_state(state=State.SYSTEM_ERROR.value)
    #        raise EngineProblem("Did not receive expected response.")
    response.pop("request", None)
    document = db_client.upsert_fields_in_root_object(
        root="run_log",
        **dict(response),
    )

    logger.info(f"[{self.request.id}] Processing completed.")
    return self.request.id
