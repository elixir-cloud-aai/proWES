"""Utility functions for POST /runs endpoint."""

import logging
from typing import Dict

from foca.config.config_parser import get_conf

from pro_wes.tasks.run_workflow import task__run_workflow

logger = logging.getLogger(__name__)


def run_workflow(
    config: Dict,
    document: Dict,
    *args,
    **kwargs
) -> Dict:
    """Executes workflow and save info to database; returns unique run id."""
    # Start workflow run in background
    __run_workflow(
        config=config,
        document=document,
        **kwargs
    )
    response = {'run_id': document['run_id']}
    return response


def __run_workflow(
    config: Dict,
    document: Dict,
    **kwargs
) -> None:
    """Helper function `run_workflow()`."""
    tes_url = get_conf(config, 'tes', 'url')
    remote_storage_url = get_conf(config, 'storage', 'remote_storage_url')
    run_id = document['run_id']
    task_id = document['task_id']
    tmp_dir = document['internal']['tmp_dir']
    cwl_path = document['internal']['cwl_path']
    param_file_path = document['internal']['param_file_path']

    # Build command
    command_list = [
        'cwl-tes',
        '--debug',
        '--leave-outputs',
        '--remote-storage-url', remote_storage_url,
        '--tes', tes_url,
        cwl_path,
        param_file_path
    ]

    # Add authorization parameters
    if 'token' in kwargs:
        auth_params = [
            '--token-public-key', get_conf(
                config,
                'security',
                'jwt',
                'public_key'
            ).encode('unicode_escape').decode('utf-8'),
            '--token', kwargs['token'],
        ]
        command_list[2:2] = auth_params

    # TEST CASE FOR SYSTEM ERROR
    # command_list = [
    #     '/path/to/non_existing/script',
    # ]
    # TEST CASE FOR EXECUTOR ERROR
    # command_list = [
    #     '/bin/false',
    # ]
    # TEST CASE FOR SLOW COMPLETION WITH ARGUMENT (NO STDOUT/STDERR)
    # command_list = [
    #     'sleep',
    #     '30',
    # ]

    # Get timeout duration
    timeout_duration = get_conf(
        config,
        'api',
        'endpoint_params',
        'timeout_run_workflow',
    )

    # Execute command as background task
    logger.info(
        (
            "Starting execution of run '{run_id}' as task '{task_id}' in "
            "'{tmp_dir}'..."
        ).format(
            run_id=run_id,
            task_id=task_id,
            tmp_dir=tmp_dir,
        )
    )
    task__run_workflow.apply_async(
        None,
        {
            'command_list': command_list,
            'tmp_dir': tmp_dir,
        },
        task_id=task_id,
        soft_time_limit=timeout_duration,
    )
    return None
