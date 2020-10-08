import json
from typing import List, Any


class Feed:
    """
    Payload object for update infos
    """

    def __init__(self, feed_id: int, user_id: str) -> None:
        self.feed_id = feed_id
        self.user_id = user_id


class Api:
    """API JSON results parser"""

    def parse_users(self, json_str: str) -> List[str]:
        """Returns a list of userIDs from JSON data"""
        try:
            users_dict = json.loads(json_str)
            return list(users_dict.keys())
        except ValueError:
            msg = 'Could not parse the JSON user list: %s' % json_str
            raise ValueError(msg)

    def parse_feeds(self, json_str: str, userID: str = None) -> List[Feed]:
        """Returns a list of feeds from JSON data"""
        try:
            feeds_json = json.loads(json_str)
            return self._parse_feeds_json(feeds_json, userID)
        except ValueError:
            msg = 'Could not parse given JSON: %s' % json_str
            raise ValueError(msg)

    def _parse_feeds_json(self, feeds: dict, userID: str) -> List[Feed]:
        feeds = feeds['feeds']
        return [Feed(info['id'], info['userId']) for info in feeds]
