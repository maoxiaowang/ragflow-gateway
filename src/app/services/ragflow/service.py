from typing import List, Optional, Tuple, Dict, Any
from urllib.parse import urljoin

from fastapi import UploadFile

from app.core.settings import settings
from app.services.ragflow.http import AsyncHTTPClient


class RAGFlowService:
    DATASETS_PATH = "/datasets"

    def __init__(self, origin_url: str, api_key: str):
        api_version = settings.ragflow.api_version
        base_url = urljoin(origin_url, f"/api/{api_version}")
        self.client = AsyncHTTPClient(base_url, api_key)

    @staticmethod
    def _clean_query_params(params: Dict[str, Any]) -> Dict[str, Any]:
        return {k: v for k, v in params.items() if v is not None}

    # ===== Dataset =====

    async def list_datasets(self, **kwargs) -> Tuple[List[Dict[str, Any]], int]:
        params = self._clean_query_params(kwargs)
        print(params)
        resp = await self.client.get(self.DATASETS_PATH, params=params)

        return (
            resp.get("data", []),
            resp.get("total_datasets", 0),
        )

    async def create_dataset(
            self,
            name: str,
            description: Optional[str] = None,
    ) -> Dict[str, Any]:
        payload = self._clean_query_params(
            {"name": name, "description": description}
        )
        resp = await self.client.post(self.DATASETS_PATH, json=payload)
        return resp.get("data", {})

    # ===== Documents =====

    async def list_documents(
            self,
            dataset_id: str,
            **kwargs,
    ) -> Tuple[List[Dict[str, Any]], int]:
        params = self._clean_query_params(kwargs)
        resp = await self.client.get(
            f"{self.DATASETS_PATH}/{dataset_id}/documents",
            params=params,
        )

        data = resp.get("data", {})
        return (
            data.get("docs", []),
            data.get("total", 0),
        )

    async def upload_documents(
            self,
            dataset_id: str,
            files: List[UploadFile],
    ) -> Tuple[List[Dict[str, Any]], int]:
        """
        批量上传文档
        """
        files_to_send = [
            ("file", (f.filename, await f.read(), f.content_type or "application/octet-stream",),)
            for f in files
        ]

        resp = await self.client.post(
            f"{self.DATASETS_PATH}/{dataset_id}/documents",
            files=files_to_send,
        )

        docs = resp.get("data", [])
        return docs, len(docs)

    async def delete_documents(
            self,
            dataset_id: str,
            document_ids: List[str],
    ):
        resp = await self.client.delete(
            f"{self.DATASETS_PATH}/{dataset_id}/documents",
            json={"ids": document_ids},
        )
        return resp

    async def delete_document_chunks(self, dataset_id: str, document_id: str, chunk_ids: List[str] = None):
        payload = {"chunk_ids": chunk_ids} if chunk_ids is not None else None
        resp = await self.client.delete(
            f"{self.DATASETS_PATH}/{dataset_id}/documents/{document_id}/chunks",
            json=payload,
        )
        return resp

    async def download_document(
            self,
            dataset_id: str,
            document_id: str,
    ):
        """
        下载文档（非 JSON 响应）
        """
        return await self.client.get(
            f"{self.DATASETS_PATH}/{dataset_id}/documents/{document_id}",
            expect_json=False,
            timeout=60,
        )

    async def parse_document_chunks(
            self,
            dataset_id: str,
            document_ids: List[str],
    ) -> Dict[str, Any]:
        resp = await self.client.post(
            f"{self.DATASETS_PATH}/{dataset_id}/chunks",
            json={"document_ids": document_ids},
        )
        return resp

    async def close(self):
        await self.client.close()


ragflow_service = RAGFlowService(
    settings.ragflow.origin_url,
    settings.ragflow.api_key,
)
