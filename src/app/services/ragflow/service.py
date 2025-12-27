from typing import List, Optional, Tuple, Dict, Any
from urllib.parse import urljoin

from fastapi import UploadFile

from app.core.settings import settings
from app.services.ragflow.http import AsyncHTTPClient


class RAGFlowService:
    def __init__(self, origin_url: str, api_key: str):
        api_version = settings.ragflow.api_version
        base_url = urljoin(origin_url, f"/api/{api_version}")
        self.client = AsyncHTTPClient(base_url, api_key)

    @staticmethod
    def _clean_query_params(params: dict[str, Any]) -> dict[str, Any]:
        return {k: v for k, v in params.items() if v is not None}

    async def list_datasets(self, **kwargs) -> Tuple[List, int]:
        """
        获取数据集列表，支持分页、排序和过滤
        """
        params = self._clean_query_params(kwargs)
        resp = await self.client.get("/datasets", params=params)
        return resp.get("data", {}), resp.get("total_datasets", 0)

    async def create_dataset(self, name: str, description: Optional[str] = None) -> Dict[str, Any]:
        """创建数据集"""
        payload = {"name": name, "description": description}
        resp = await self.client.post("/datasets", json=payload)
        return resp.get("data", {})

    # async def get_dataset(self, dataset_id: int) -> Dict[str, Any]:
    #     """获取单个数据集"""
    #     try:
    #         resp = await self.client.get(f"/datasets/{dataset_id}")
    #         return resp.get("data", {})
    #     except RAGFlowError as e:
    #         raise

    # async def update_dataset(self, dataset_id: int, data: Dict[str, Any]) -> Dict[str, Any]:
    #     """更新数据集"""
    #     try:
    #         resp = await self.client.put(f"/datasets/{dataset_id}", json=data)
    #         return resp.get("data", {})
    #     except RAGFlowError as e:
    #         raise
    #
    # async def delete_dataset(self, dataset_id: int) -> Dict[str, Any]:
    #     """删除数据集"""
    #     try:
    #         resp = await self.client.delete(f"/datasets/{dataset_id}")
    #         return resp.get("data", {})
    #     except RAGFlowError as e:
    #         raise

    async def list_documents(self, dataset_id: str, **kwargs) -> Tuple[List, int]:
        params = self._clean_query_params(kwargs)
        resp = await self.client.get(f"/datasets/{dataset_id}/documents", params=params)
        data = resp.get("data", {})
        return data.get("docs", []), data.get("total", 0)

    async def upload_document(self, dataset_id: str, files: List[UploadFile]):
        files_to_send = [
            ("file", (f.filename, await f.read(), f.content_type or "application/octet-stream"))
            for f in files
        ]

        resp = await self.client.post(f"/datasets/{dataset_id}/documents", files=files_to_send)
        docs = resp.get("data", [])
        return docs, len(docs)

    async def close(self):
        await self.client.close()


ragflow_service = RAGFlowService(
    settings.ragflow.origin_url,
    settings.ragflow.api_key
)
