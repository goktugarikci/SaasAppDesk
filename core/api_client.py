# core/api_client.py
import requests
from core import config

class ApiClient:
    def __init__(self):
        self.session = requests.Session()

    def _get_headers(self):
        headers = {"Content-Type": "application/json"}
        if config.CURRENT_TOKEN:
            # C++ backend'in beklediği Authorization formatı
            headers["Authorization"] = config.CURRENT_TOKEN
        return headers

    def get(self, endpoint):
        url = f"{config.BASE_API_URL}/{endpoint}"
        response = self.session.get(url, headers=self._get_headers())
        return response

    def post(self, endpoint, data=None):
        url = f"{config.BASE_API_URL}/{endpoint}"
        response = self.session.post(url, json=data, headers=self._get_headers())
        return response
        
    def put(self, endpoint, data=None):
        url = f"{config.BASE_API_URL}/{endpoint}"
        response = self.session.put(url, json=data, headers=self._get_headers())
        return response

    def delete(self, endpoint):
        url = f"{config.BASE_API_URL}/{endpoint}"
        response = self.session.delete(url, headers=self._get_headers())
        return response