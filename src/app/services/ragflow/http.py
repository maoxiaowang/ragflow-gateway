import logging
from pathlib import PurePosixPath
from urllib.parse import urljoin

import httpx

from .exceptions import (
    RAGFlowRequestError, RAGFlowTimeoutError, RAGFlowResponseError, RAGFlowUnavailableError,
    RAGFlowError
)

logger = logging.getLogger(__name__)


class AsyncHTTPClient:
    def __init__(self, base_url: str, api_key, timeout=5):
        self._client = httpx.AsyncClient(
            timeout=timeout,
            headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        )
        self.base_url = base_url.rstrip("/")

    async def _request(self, method, path, **kwargs):
        url = self.base_url + '/' + path.lstrip('/')
        try:
            resp = await self._client.request(method, url, **kwargs)
            resp.raise_for_status()
            data = resp.json()
            if data.get("code") != 0:
                raise RAGFlowResponseError(f"RAGFlow code error: {data.get('message')}")
            return data
        except httpx.ReadTimeout as e:
            raise RAGFlowTimeoutError("RAGFlow request timed out") from e
        except httpx.RequestError as e:
            raise RAGFlowRequestError(f"RAGFlow request failed: {e}") from e
        except httpx.HTTPStatusError as e:
            status = e.response.status_code
            if status >= 500:
                raise RAGFlowUnavailableError(f"RAGFlow HTTP error {status}") from e
            else:
                raise RAGFlowRequestError(f"RAGFlow HTTP error {status}") from e
        except Exception as e:
            logger.error(f"RAGFlow request failed: {e}")
            raise RAGFlowError(f"Unexpected error: {e}") from e

    async def get(self, path, params=None, json=None):
        return await self._request("GET", path, params=params, json=json)

    async def post(self, path, json=None, files=None):
        return await self._request("POST", path, json=json, files=files)

    async def put(self, path, json=None):
        return await self._request("PUT", path, json=json)

    async def delete(self, path, json=None):
        return await self._request("DELETE", path, json=json)

    async def close(self):
        await self._client.aclose()