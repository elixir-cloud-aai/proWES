"""Controller for service info endpoint."""

import logging

from flask import current_app
from typing import Dict

from pro_wes.exceptions import (
    NotFound,
    ValidationError,
)
from pro_wes.ga4gh.wes.states import States

logger = logging.getLogger(__name__)


class RegisterServiceInfo:
    """Tool class for registering service info.

    Creates service info upon first request, if it does not exist.
    """

    def __init__(self) -> None:
        """Initialize class requirements.

        Attributes:
            conf_info: Service info details as per enpoints config.
            coll_info: Database collection storing service info objects.
            coll_runs: Database collection storing workflow run objects.
        """
        self.conf_info = current_app.config['FOCA'].endpoints['service_info']
        db = current_app.config['FOCA'].db.dbs['runStore']
        self.coll_info = db.collections['service_info'].client
        self.coll_runs = db.collections['runs'].client

    def get_service_info(self) -> Dict:
        """Get latest service info from database.

        Returns:
            Latest service info details.

        Raises:
            NotFound: Service info was not found.
        """
        try:
            service_info = self.coll_info.find(
                {},
                {'_id': False}
            ).sort([('_id', -1)]).limit(1).next()
        except StopIteration:
            raise NotFound
        service_info['system_state_counts'] = self._get_system_state_counts()
        return service_info

    def set_service_info_from_config(
            self,
    ) -> None:
        """Create or update service info from service configuration.

        Will create service info if it does not exist or current
        configuration differs from available one.

        Raises:
            pro_wes.exceptions.ValidationError: Service info
                configuration does not conform to API specification.
        """
        try:
            db_info = self.get_service_info()
        except NotFound:
            db_info = {}
        if db_info != self.conf_info:
            try:
                self._upsert_service_info(data=self.conf_info)
            except KeyError:
                logger.exception(
                    "The service info configuration does not conform to the "
                    "API specification."
                )
                raise ValidationError
            logger.info(
                "Service info registered."
            )
        else:
            logger.info(
                "Using available service info."
            )

    def _upsert_service_info(
            self,
            data: Dict,
    ) -> None:
        """Insert or updated service info document."""
        self.coll_info.replace_one(
            filter={'id': data['id']},
            replacement=data,
            upsert=True,
        )

    def set_service_info_from_app_context(
        self,
        data: Dict,
    ) -> Dict:
        """Return service info.

        Arguments:
            data: Service info according to API specification.

        Returns:
            Response headers.
        """
        self._upsert_service_info(data=data)
        return self._get_headers()

    def _get_headers(self) -> Dict:
        """Build dictionary of response headers.

        Returns:
            Response headers.
        """
        headers: Dict = {
            'Content-type': 'application/json',
        }
        return headers

    def _get_system_state_counts(self) -> Dict[str, int]:
        """Gets current system state counts."""
        current_counts = self._init_system_state_counts()

        # Query database for workflow run states
        cursor = self.coll_runs.find(
            filter={},
            projection={
                'api.state': True,
                '_id': False,
            }
        )

        # Iterate over states and increase counter
        for record in cursor:
            current_counts[record['api']['state']] += 1

        return current_counts

    @staticmethod
    def _init_system_state_counts() -> Dict[str, int]:
        """Initializes system state counts."""
        # TODO: Get states programmatically or define as enum
        # Set all state counts to zero
        return {state: 0 for state in States.ALL}
