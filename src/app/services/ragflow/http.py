import os

import httpx
from sqlalchemy.util import await_only

from .exceptions import RequestError

class AsyncHTTPClient:
    def __init__(self, base_url: str, api_key: str = None, timeout=30):
        self._client = httpx.AsyncClient(
            base_url=base_url,
            timeout=timeout,
            headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        )

    async def _request(self, method, path, **kwargs):
        print("path", path)
        try:
            resp = await self._client.request(method, path, **kwargs)
            resp.raise_for_status()
            data = resp.json()
            if data.get("code") != 0:
                raise RequestError(f"code error: {data.get('message')}")
            return data
        except httpx.ReadTimeout as e:
            raise RequestError(f"Request timed out") from e
        except httpx.RequestError as e:
            raise RequestError(f"Request failed: {e}") from e
        except httpx.HTTPStatusError as e:
            raise RequestError(f"HTTP error {e.response.status_code}: {e}") from e
        except Exception as e:
            raise RequestError(f"Unexpected error: {e}") from e

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