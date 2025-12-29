import logging
from typing import Any, Optional, Tuple, List

import httpx

from .exceptions import (
    RAGFlowRequestError,
    RAGFlowTimeoutError,
    RAGFlowResponseError,
    RAGFlowUnavailableError,
    RAGFlowError,
)

logger = logging.getLogger(__name__)


class AsyncHTTPClient:
    def __init__(
            self,
            base_url: str,
            api_key: str,
            timeout: float = 5.0,
    ):
        self.base_url = base_url.rstrip("/")
        self._client = httpx.AsyncClient(
            timeout=httpx.Timeout(timeout),
            trust_env=False,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Accept": "application/json",
            },
        )

    def _build_url(self, path: str) -> str:
        return f"{self.base_url}/{path.lstrip('/')}"

    async def _request(
            self,
            method: str,
            path: str,
            *,
            expect_json: bool = True,
            **kwargs: Any,
    ) -> Any:
        url = self._build_url(path)

        try:
            resp = await self._client.request(method, url, **kwargs)
            resp.raise_for_status()

            if not expect_json:
                return resp

            data = resp.json()

            # 业务层错误
            if not isinstance(data, dict):
                raise RAGFlowResponseError("Invalid JSON response")

            if data.get("code") != 0:
                print(data)
                raise RAGFlowResponseError(
                    f"RAGFlow error: {data.get('message', 'Unknown error')}"
                )

            return data

        except httpx.ReadTimeout as e:
            logger.warning("RAGFlow request timeout: %s %s", method, url)
            raise RAGFlowTimeoutError("RAGFlow request timed out") from e

        except httpx.HTTPStatusError as e:
            status = e.response.status_code
            logger.error(
                "RAGFlow HTTP error %s %s -> %s",
                method,
                url,
                status,
            )
            if status >= 500:
                raise RAGFlowUnavailableError(
                    f"RAGFlow service unavailable ({status})"
                ) from e
            raise RAGFlowRequestError(
                f"RAGFlow HTTP error ({status})"
            ) from e

        except httpx.RequestError as e:
            logger.exception(
                "RAGFlow request failed: %s %s",
                method,
                url,
            )
            raise RAGFlowRequestError(
                f"RAGFlow request failed: {e}"
            ) from e

        except Exception as e:
            logger.exception("Unexpected RAGFlow error")
            raise RAGFlowError(f"Unexpected error: {e}") from e

    # ===== HTTP verbs =====

    async def get(
            self,
            path: str,
            *,
            params: Optional[dict] = None,
            expect_json: bool = True,
            **kwargs: Any,
    ):
        return await self._request(
            "GET",
            path,
            params=params,
            expect_json=expect_json,
            **kwargs,
        )

    async def post(
            self,
            path: str,
            *,
            json: Optional[dict] = None,
            files: Optional[List[Tuple[str, Tuple[str, bytes, Optional[str]]]]] = None,
            expect_json: bool = True,
            **kwargs: Any,
    ):
        return await self._request(
            "POST",
            path,
            json=json,
            files=files,
            expect_json=expect_json,
            **kwargs,
        )

    async def put(
            self,
            path: str,
            *,
            json: Optional[dict] = None,
            **kwargs: Any,
    ):
        return await self._request("PUT", path, json=json, **kwargs)

    async def delete(
            self,
            path: str,
            *,
            json: Optional[dict] = None,
            **kwargs: Any,
    ):
        return await self._request("DELETE", path, json=json, **kwargs)

    async def close(self):
        await self._client.aclose()
