from __future__ import annotations

import logging
from urllib.parse import urlsplit, urlunsplit

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from settings import settings

logger = logging.getLogger(__name__)


class RequestUtil:
    """Small HTTP client shared by the API tests.

    A shared session keeps connection pooling effective because the existing
    tests create a short-lived ``RequestUtil`` object for each request.
    Retries are limited to transient connection/server failures and never retry
    POST requests.
    """

    _session: requests.Session | None = None

    def __init__(self, timeout: float | None = None):
        self.timeout = settings.api_timeout if timeout is None else timeout
        if self.__class__._session is None:
            session = requests.Session()
            retry = Retry(
                total=2,
                connect=2,
                read=2,
                status=2,
                backoff_factor=0.2,
                status_forcelist=(502, 503, 504),
                allowed_methods=frozenset({"GET", "HEAD", "OPTIONS"}),
                raise_on_status=False,
            )
            adapter = HTTPAdapter(max_retries=retry)
            session.mount("http://", adapter)
            session.mount("https://", adapter)
            self.__class__._session = session
        self.session = self.__class__._session

    @staticmethod
    def _rewrite_url(url: str) -> str:
        """Use API_BASE_URL while preserving the path in YAML test data."""
        configured = urlsplit(settings.api_base_url)
        original = urlsplit(url)
        if not configured.scheme or not configured.netloc:
            raise ValueError("API_BASE_URL must include a scheme and host")
        return urlunsplit(
            (
                configured.scheme,
                configured.netloc,
                original.path,
                original.query,
                original.fragment,
            )
        )

    def send_all_request(self, token: str | None = None, **kwargs):
        if "url" not in kwargs:
            raise ValueError("request must include a url")
        kwargs["url"] = self._rewrite_url(kwargs["url"])
        headers = dict(kwargs.pop("headers", {}) or {})
        if token:
            headers["Authorization"] = f"Bearer {token}"
        if headers:
            kwargs["headers"] = headers
        kwargs.setdefault("timeout", self.timeout)
        logger.info("%s %s", kwargs.get("method", "GET"), kwargs["url"])
        try:
            response = self.session.request(**kwargs)
        except requests.RequestException:
            logger.exception(
                "HTTP request failed: %s %s", kwargs.get("method", "GET"), kwargs["url"]
            )
            raise
        logger.info("HTTP response: %s", response.status_code)
        return response

    def close(self):
        # Keep the shared pool alive for the rest of the test session.
        return None

    @classmethod
    def close_shared_session(cls):
        if cls._session is not None:
            cls._session.close()
            cls._session = None

    def __enter__(self):
        return self

    def __exit__(self, *_exc):
        self.close()
