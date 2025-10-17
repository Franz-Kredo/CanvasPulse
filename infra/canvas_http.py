

# infra/canvas_http.py
from requests import Response, Session, RequestException

from urllib.parse import urljoin
from typing import Iterable, Any, Optional
from core.ports import ICanvasClient  # import your interface

class CanvasHTTPClient(ICanvasClient):
    """Concrete implementation that talks to the real Canvas API."""

    def __init__(self, base_url: str, token: str):
        self.base_url = base_url
        self._session = self.__create_session(token)

    def __create_session(self, token):
        """Initializes a requests session with authentication headers."""
        session = Session()
        session.headers.update({
            "Accept": "application/json",
            "Authorization": f"Bearer {token}",
        })
        return session


    def get_paginated(self, path: str, params: Optional[dict] = None) -> Iterable[Any]:
        """Implements the abstract method — actually fetches pages from the API."""
        ret_data = list()
        url = urljoin(self.base_url, path)
        
        while url:
            try:
                resp: Response = self._session.get(url, params=params)
                resp.raise_for_status()
                data = resp.json()

                if isinstance(data, list):
                    ret_data.extend(data)   
                else:
                    ret_data.append(data)   

                # Get the URL for the next page from the 'Link' header
                url = resp.links.get("next", {}).get("url")
                # Following requests use the full URL, therefore params is not needed
                params = None 
            except RequestException as e:
                print(f"API request failed: {e}")
                break
        
        return ret_data