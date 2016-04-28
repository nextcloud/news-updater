import json


class Feed:
    """
    Payload object for update infos
    """

    def __init__(self, feedId, userId):
        self.feedId = feedId
        self.userId = userId


class Api:
    def parse_feed(self, json_string):
        """
        Wrapper around json.loads for better error messages
        """
        try:
            feed_json = json.loads(json_string)
            feed_json = feed_json['feeds']
            return [Feed(info['id'], info['userId']) for info in feed_json]
        except ValueError:
            msg = "Could not parse given JSON: %s" % json_string
            raise ValueError(msg)
