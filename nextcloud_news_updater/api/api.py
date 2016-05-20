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
    def parse_feed(self, json_string: str) -> List[Feed]:
        """
        Wrapper around json.loads for better error messages
        """
        try:
            feed_json = json.loads(json_string)
            return self._parse_json(feed_json)
        except ValueError:
            msg = "Could not parse given JSON: %s" % json_string
            raise ValueError(msg)

    def _parse_json(self, feed_json: Any) -> List[Feed]:
        feed_json = feed_json['feeds']
        return [Feed(info['id'], info['userId']) for info in feed_json]
