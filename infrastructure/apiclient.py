import json
import logging
import requests
from urllib.parse import urlencode
from copy import deepcopy

from config.config import WMS_API_BASE_URL

logger = logging.getLogger(__name__)


class ApiClient:
    def __init__(self, prefix_url: str):
        self.prefix_url = prefix_url

    def _create_url(self, endpoint: str, query: dict = None) -> str:
        if query:
            params = urlencode(query)
            return self.prefix_url + endpoint + "?" + params
        return self.prefix_url + endpoint

    def fetch_lists(self, query: dict) -> requests.Response:
        url = self._create_url("api/v1/lists/", query)
        response = requests.get(url=url)
        logger.info(response.text)
        return response

    def fetch_gachas(self, query: dict, list_id, kind) -> requests.Response:
        url = self._create_url(f"api/v1/lists/{list_id}/gacha/{kind}", query)
        response = requests.get(url=url)
        logger.info(response.text)
        return response


apiClient = ApiClient(
    prefix_url=WMS_API_BASE_URL,
)
