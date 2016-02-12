__author__ = 'ujjwal'
import requests
from priceprobi.config import OGD_API_KEY, OGD_API_URL, MANDI_PRICES_RESOURCE_ID, get_config
from priceprobi.utils import get_env
from priceprobi.db.mongo_helper import MongoHelper


class OGDRequest:

    """
        https://data.gov.in/resources/current-daily-price-various-commodities-various-markets-mandis/api
    """
    def __init__(self, resource_id):
        self._resource_id = resource_id
        self._api_key = OGD_API_KEY
        self._url = OGD_API_URL

    def get(self, offset=0, limit=100, filters={}):
        params = {
            "resource_id": self._resource_id,
            "api-key": self._api_key,
            "offset": offset,
            "limit": limit
        }

        if len(filters):
            params["filters"] = filters

        req = requests.get(self._url, params=params)
        resp = req.json()
        return resp


def run_ingest(config):
    ogd_request = OGDRequest(resource_id=MANDI_PRICES_RESOURCE_ID)
    mongo_helper = MongoHelper(config)

    offset = 0
    limit = 100
    max_count = 0

    resp = ogd_request.get(offset, limit)
    mongo_helper.save(resp["records"])

    offset += limit
    while resp["count"] == limit:
        resp = ogd_request.get(offset, limit)
        mongo_helper.save(resp["records"])
        offset += limit

        if (max_count > 0) and (offset+limit > max_count):
            break

if __name__ == "__main__":
    config = get_config(env=get_env())
    run_ingest(config)
