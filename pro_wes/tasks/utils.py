"""Utility functions for Celery background tasks."""

import logging
from typing import Optional

from pymongo import collection as Collection
from pymongo.errors import PyMongoError

from pro_wes.utils.db import DbDocumentConnector


# Get logger instance
logger = logging.getLogger(__name__)


def set_run_state(
    collection: Collection,
    run_id: str,
    task_id: Optional[str] = None,
    state: str = "UNKNOWN",
):
    """Set/update state of run associated with Celery task."""
    if not task_id:
        document = collection.find_one(
            filter={"run_id": run_id},
            projection={
                "task_id": True,
                "_id": False,
            },
        )
        _task_id = document["task_id"]
    else:
        _task_id = task_id
    try:
        db = DbDocumentConnector(
            collection=collection,
            task_id=_task_id,
        )
        db.update_run_state(state=state)
    except PyMongoError as exc:
        logger.exception(
            f"Database error. Could not update state of run '{run_id}' "
            f"(task id: '{task_id}') to state '{state}'. Original error "
            f"message: {type(exc).__name__}: {exc}"
        )
    finally:
        if document:
            logger.info(
                f"State of run '{run_id}' (task id: '{task_id}') "
                f"changed to '{state}'."
            )
