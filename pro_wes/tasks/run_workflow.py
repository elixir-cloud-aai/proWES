"""Celery background task to start workflow run."""

import logging
from typing import (List, Tuple)

from pro_wes.worker import celery


# Get logger instance
logger = logging.getLogger(__name__)


@celery.task(
    name='tasks.run_workflow',
    bind=True,
    ignore_result=True,
    track_started=True
)
def task__run_workflow(
    self,
    command_list: List,
    tmp_dir: str
) -> Tuple[int, List[str], List[str]]:
    """Adds workflow run to task queue."""
    # wes_state = 'UNKNOWN'

    # Start workflow run
    # wes_id = 'ID'  # TODO: Implement

    # Poll run status
    # while wes_state not in COMPLETE_STATES:
    # TODO: Implement
    # celery.Task.send_event(
    #     'task-wes-run-state-update',
    #     wes_id='',
    #     wes_state='',
    # )
