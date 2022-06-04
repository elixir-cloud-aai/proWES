"""Celery background task to cancel workflow run and related TES tasks."""

import logging

# from celery.exceptions import SoftTimeLimitExceeded
# from celery import current_app
# from foca.database.register_mongodb import create_mongo_client

from pro_wes.worker import celery
# from pro_wes.tasks.utils import set_run_state


# Get logger instance
logger = logging.getLogger(__name__)


@celery.task(
    name='tasks.cancel_run',
    ignore_result=True,
    bind=True,
)
def task__cancel_run(
    self,
    run_id: str,
    task_id: str,
) -> None:
    """Revokes worfklow task and tries to cancel all running TES tasks."""
    # try:
    #     config = current_app.config
    #     # Create MongoDB client
    #     mongo = create_mongo_client(
    #         app=current_app,
    #         config=config,
    #     )
    #     collection = mongo.db['runs']
    #     # Set run state to 'CANCELING'
    #     set_run_state(
    #         collection=collection,
    #         run_id=run_id,
    #         task_id=task_id,
    #         state='CANCELING',
    #     )
    #     # Cancel WES run
    #     # TODO: Implement

    # except SoftTimeLimitExceeded as e:
    #     set_run_state(
    #         collection=collection,
    #         run_id=run_id,
    #         task_id=task_id,
    #         state='SYSTEM_ERROR',
    #     )
    #     logger.warning(
    #         (
    #             "Canceling workflow run '{run_id}' timed out. Run state "
    #             "was set to 'SYSTEM_ERROR'. Original error message: "
    #             "{type}: {msg}"
    #         ).format(
    #             run_id=run_id,
    #             type=type(e).__name__,
    #             msg=e,
    #         )
    #     )
