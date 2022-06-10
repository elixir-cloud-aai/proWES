"""Controller for service info endpoint."""

import logging

from bson.objectid import ObjectId
from flask import current_app
from typing import Dict

from pro_wes.exceptions import (
    NotFound,
)
from pro_wes.ga4gh.wes.states import States

logger = logging.getLogger(__name__)


class ServiceInfo:
    """Tool class for registering service info.

    Creates service info upon first request, if it does not exist.
    """

    def __init__(self) -> None:
        """Initialize class requirements.

        Attributes:
            config: App configuration.
            object_id: Database identifier for service info.
            coll_info: Database collection storing service info objects.
            coll_runs: Database collection storing workflow run objects.
        """
        self.config = current_app.config
        self.object_id = "000000000000000000000000"
        db = self.config['FOCA'].db.dbs['runStore']
        self.coll_info = db.collections['service_info'].client
        self.coll_runs = db.collections['runs'].client

    def get_service_info(self) -> Dict:
        """Get latest service info from database.

        Returns:
            Latest service info details.

        Raises:
            NotFound: Service info was not found.
        """
        service_info = self.coll_info.find_one(
            {'_id': ObjectId(self.object_id)},
            {'_id': False},
        )
        if service_info is None:
            raise NotFound
        service_info['system_state_counts'] = self._get_system_state_counts()
        return service_info

    def set_service_info(
        self,
        data: Dict,
    ) -> None:
        """Create or update service info.

        Arguments:
            data: Dictionary of service info values. Cf.
        """
        self.coll_info.replace_one(
            filter={'_id': ObjectId(self.object_id)},
            replacement=data,
            upsert=True,
        )
        logger.info("Service info set.")

    def _get_system_state_counts(self) -> Dict[str, int]:
        """Gets current system state counts."""
        current_counts = {state: 0 for state in States.ALL}
        cursor = self.coll_runs.find(
            filter={},
            projection={
                'api.state': True,
                '_id': False,
            }
        )
        for record in cursor:
            current_counts[record['api']['state']] += 1
        return current_counts
