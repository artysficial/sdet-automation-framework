"""Client for the YouTube Data API v3. The API key is sent as a query parameter."""

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


class YouTubeClient:

    def __init__(self, base_url: str, api_key: str, timeout: int = 30):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.timeout = timeout
        self.session = requests.Session()
        retry = Retry(total=3, backoff_factor=1, status_forcelist=[500, 502, 503, 504], allowed_methods=None)
        self.session.mount("https://", HTTPAdapter(max_retries=retry))

    def _get(self, resource: str, params: dict) -> requests.Response:
        return self.session.get(f"{self.base_url}/{resource}",
                                params={**params, "key": self.api_key}, timeout=self.timeout)

    def search(self, query: str, max_results: int = 5, **params) -> requests.Response:
        return self._get("search", {"part": "snippet", "q": query, "maxResults": max_results,
                                     "type": "video", **params})

    def video(self, video_id: str, part: str = "snippet,statistics,contentDetails") -> requests.Response:
        return self._get("videos", {"part": part, "id": video_id})

    def channel(self, channel_id: str, part: str = "snippet,statistics") -> requests.Response:
        return self._get("channels", {"part": part, "id": channel_id})

    def playlist_items(self, playlist_id: str, max_results: int = 10) -> requests.Response:
        return self._get("playlistItems", {"part": "snippet", "playlistId": playlist_id,
                                            "maxResults": max_results})
