# tests/integration/test_canvas_api_live.py
import os
import pytest
from dotenv import load_dotenv
from infra.canvas_http import CanvasHTTPClient
from requests.exceptions import RequestException

# Load .env from project root
load_dotenv()

@pytest.mark.live
def test_canvas_api_token_validity():
    """Checks if the real Canvas API token in .env works."""
    base_url = os.getenv("CANVAS_BASE_URL", "https://reykjavik.instructure.com/")
    token = os.getenv("CANVAS_TOKEN")

    assert token, "Missing CANVAS_TOKEN in .env — cannot run live test."

    client = CanvasHTTPClient(base_url, token)

    try:
        # A lightweight call that doesn't change anything
        courses = client.get_paginated("/api/v1/courses", params={"per_page": 1})
        assert courses, "API call succeeded but returned empty data."
        print(f"✅ Token appears valid — fetched {len(courses)} item(s).")
    except RequestException as e:
        pytest.fail(f"Canvas API call failed: {e}")
