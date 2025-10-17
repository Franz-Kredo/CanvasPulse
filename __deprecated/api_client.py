# api_client.py
"""
A client for interacting with the Canvas LMS API.
Handles authentication, session management, and pagination.
"""
import warnings
from typing import Iterator, Any
from urllib.parse import urljoin

import requests
from requests import Response, Session

# Suppress UserWarning from instructure-canvas-python library if used
warnings.filterwarnings("ignore", category=UserWarning)

class CanvasAPIClient:
    """A simple client for the Canvas API."""

    def __init__(self, base_url: str, api_token: str):
        self.base_url = base_url
        self._session = self._create_session(api_token)

    def _create_session(self, api_token: str) -> Session:
        """Initializes a requests session with authentication headers."""
        session = requests.Session()
        session.headers.update({
            "Accept": "application/json",
            "Authorization": f"Bearer {api_token}",
        })
        return session

    def get_paginated(self, path: str, params: dict = None) -> Iterator[Any]:
        """
        Yields all items from a paginated Canvas API endpoint.
        
        Args:
            path: The API endpoint path (e.g., "/api/v1/courses").
            params: A dictionary of query parameters for the request.
        """
        url = urljoin(self.base_url, path)
        while url:
            try:
                resp: Response = self._session.get(url, params=params)
                resp.raise_for_status()
                data = resp.json()

                if isinstance(data, list):
                    yield from data
                else:
                    yield data # For non-list single-page results

                # Get the URL for the next page from the 'Link' header
                url = resp.links.get("next", {}).get("url")
                params = None # Subsequent requests use the full URL from 'next'
            except requests.RequestException as e:
                print(f"API request failed: {e}")
                break