
from infra.canvas_http import CanvasHTTPClient
from requests import RequestException


class FakeResponse:
    def __init__(self, payload, next_url=None):
        """
        payload: list[...]  or dict (single-object page)
        next_url: absolute URL to the next page, or None
        """
        self._payload = payload
        self.links = {"next": {"url": next_url}} if next_url else {}

    def raise_for_status(self):
        # Simulate successful responses
        return None

    def json(self):
        return self._payload


class FakeSession:
    """
    A simple scriptable Session:
      - Provide a list of responses or exceptions to pop
      - Records calls for assertions
    """
    def __init__(self, script):
        self.script = list(script)  # list of FakeResponse or Exception
        self.calls = []             # list of (url, params)

    def get(self, url, params=None):
        self.calls.append((url, params))
        nxt = self.script.pop(0)
        if isinstance(nxt, Exception):
            raise nxt
        return nxt


# ##=========== Tests ===========## #
def test_get_paginated_collects_across_pages_and_returns_list():
    # Page 1 (two items) -> next -> Page 2 (one item) -> end
    page1 = FakeResponse(payload=[{"id": 1}, {"id": 2}],
                         next_url="https://api/courses?page=2")

    page2 = FakeResponse(payload=[{"id": 3}],
                         next_url=None)

    client = CanvasHTTPClient(base_url="https://api/", token="X")
    client._session = FakeSession([page1, page2])  # overwrite internal session

    items = client.get_paginated("/api/v1/courses", params={"per_page": 2})
    # Your current implementation returns a list (not a generator)
    assert [i["id"] for i in items] == [1, 2, 3]

    # Assert first call used params; second followed next link (params=None)
    calls = client._session.calls
    assert calls[0][0].endswith("/api/v1/courses")
    assert calls[0][1] == {"per_page": 2}
    assert calls[1][0] == "https://api/courses?page=2"
    assert calls[1][1] is None


def test_get_paginated_supports_single_object_pages():
    # First page=single object (Canvas can return dict for single-page endpts)
    page1 = FakeResponse({"id": 42, "name": "Single"}, next_url=None)

    client = CanvasHTTPClient(base_url="https://api/", token="X")
    client._session = FakeSession([page1])

    items = client.get_paginated("/api/v1/something")
    assert isinstance(items, list)
    assert items == [{"id": 42, "name": "Single"}]


def test_get_paginated_stops_on_request_exception_and_returns_partial():
    # First page fine, second raises network error
    page1 = FakeResponse([{"id": 1}], next_url="https://api/next")
    boom = RequestException("network down")

    client = CanvasHTTPClient(base_url="https://api/", token="X")
    client._session = FakeSession([page1, boom])

    items = client.get_paginated("/api/v1/courses")
    # Your implementation prints and breaks -> returns what it collected so far
    assert items == [{"id": 1}]

    calls = client._session.calls
    assert len(calls) == 2
    assert calls[0][0].endswith("/api/v1/courses")
    assert calls[1][0] == "https://api/next"


def test_get_paginated_handles_empty_pages():
    # API returns empty list and no next
    page1 = FakeResponse([], next_url=None)

    client = CanvasHTTPClient(base_url="https://api/", token="X")
    client._session = FakeSession([page1])

    items = client.get_paginated("/api/v1/empty")
    assert items == []
