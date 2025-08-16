from unittest.mock import Mock

from app.services.situation_service import SituationService


def test_feed_pagination_normalization():
    repo = Mock()
    service = SituationService(repo=repo)
    repo.get_situations_feed.return_value = []
    service.get_situations_feed_paginated(page=0, limit=150, current_user_id=None)
    repo.get_situations_feed.assert_called_once_with(
        limit=10, offset=0, current_user_id=None
    )
