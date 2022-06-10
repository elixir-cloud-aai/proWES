
"""Controllers for the `/runs` and children routes."""

import logging
from typing import Dict

from bson.objectid import ObjectId

from pro_wes.exceptions import (
    Forbidden,
    RunNotFound,
)

# Get logger instance
logger = logging.getLogger(__name__)


# Utility function for endpoint GET /runs
def list_runs(
    config: Dict,
    *args,
    **kwargs
) -> Dict:
    """Lists IDs and status for all workflow runs."""
    coll_runs = config['FOCA'].db.dbs['runStore'].collections['runs'].client

    # Fall back to default page size if not provided by user
    if 'page_size' in kwargs:
        page_size = kwargs['page_size']
    else:
        page_size = config['FOCA'].endpoints['global']['default_page_size']

    # Extract/set page token
    if 'page_token' in kwargs:
        page_token = kwargs['page_token']
    else:
        page_token = ''

    # Initialize filter dictionary
    filter_dict = {}

    # Add filter for user-owned runs if user ID is available
    if 'user_id' in kwargs:
        filter_dict['user_id'] = kwargs['user_id']

    # Add pagination filter based on last object ID
    if page_token != '':
        filter_dict['_id'] = {'$lt': ObjectId(page_token)}

    # Query database for workflow runs
    cursor = coll_runs.find(
        filter=filter_dict,
        projection={
            'run_id': True,
            'api.state': True,
        }
        # Sort results by descending object ID (+/- newest to oldest)
        ).sort(
            '_id', -1
        # Implement page size limit
        ).limit(
            page_size
        )

    # Convert cursor to list
    runs_list = list(cursor)

    # Get next page token from ID of last run in cursor
    if runs_list:
        next_page_token = str(runs_list[-1]['_id'])
    else:
        next_page_token = ''

    # Reshape list of runs
    for run in runs_list:
        del run['_id']
        run['state'] = run['api']['state']
        del run['api']

    # Build and return response
    return {
        'next_page_token': next_page_token,
        'runs': runs_list
    }


# Utility function for endpoint GET /runs/<run_id>
def get_run_log(
    config: Dict,
    run_id: str,
    *args,
    **kwargs
) -> Dict:
    """Gets detailed log information for specific run."""
    coll_runs = config['FOCA'].db.dbs['runStore'].collections['runs'].client
    document = coll_runs.find_one(
        filter={'run_id': run_id},
        projection={
            'user_id': True,
            'api': True,
            '_id': False,
        }
    )

    # Raise error if workflow run was not found or has no task ID
    if document:
        run_log = document['api']
    else:
        logger.error("Run '{run_id}' not found.".format(run_id=run_id))
        raise RunNotFound

    # Raise error trying to access workflow run that is not owned by user
    # Only if authorization enabled
    if 'user_id' in kwargs and document['user_id'] != kwargs['user_id']:
        logger.error(
            (
                "User '{user_id}' is not allowed to access workflow run "
                "'{run_id}'."
            ).format(
                user_id=kwargs['user_id'],
                run_id=run_id,
            )
        )
        raise Forbidden

    return run_log


# Utility function for endpoint GET /runs/<run_id>/status
def get_run_status(
    config: Dict,
    run_id: str,
    *args,
    **kwargs
) -> Dict:
    """Gets status information for specific run."""
    coll_runs = config['FOCA'].db.dbs['runStore'].collections['runs'].client
    document = coll_runs.find_one(
        filter={'run_id': run_id},
        projection={
            'user_id': True,
            'api.state': True,
            '_id': False,
        }
    )

    # Raise error if workflow run was not found or has no task ID
    if document:
        state = document['api']['state']
    else:
        logger.error("Run '{run_id}' not found.".format(run_id=run_id))
        raise RunNotFound

    # Raise error trying to access workflow run that is not owned by user
    # Only if authorization enabled
    if 'user_id' in kwargs and document['user_id'] != kwargs['user_id']:
        logger.error(
            (
                "User '{user_id}' is not allowed to access workflow run "
                "'{run_id}'."
            ).format(
                user_id=kwargs['user_id'],
                run_id=run_id,
            )
        )
        raise Forbidden

    response = {
        'run_id': run_id,
        'state': state
    }
    return response
