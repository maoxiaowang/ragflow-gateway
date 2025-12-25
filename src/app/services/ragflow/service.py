from typing import List, Optional, Tuple
from urllib.parse import urljoin

from app.core.settings import settings
from app.services.ragflow.exceptions import RAGFlowError
from app.services.ragflow.http import AsyncHTTPClient


class RAGFlowService:
    def __init__(self, origin_url: str, api_key: str):
        api_version = settings.ragflow.api_version
        base_url = urljoin(origin_url, f"/api/{api_version}")
        self.client = AsyncHTTPClient(base_url, api_key)

    async def list_datasets(
            self,
            page: int = 1,
            page_size: int = 30,
            order_by: Optional[str] = "create_time",
            desc: bool = True,
            name: Optional[str] = None,
            _id: Optional[int] = None,
    ) -> Tuple[List, int]:
        """
        获取数据集列表，支持分页、排序和过滤
        """
        params = {
            "page": page,
            "page_size": page_size,
            "orderby": order_by,
            "desc": desc,
            "name": name,
            "id": _id,
        }

        params = {k: v for k, v in params.items() if v is not None}
        try:
            resp = await self.client.get("/datasets", params=params)
            return resp.get("data", {}), resp.get("total_datasets", 0)
        except RAGFlowError as e:
            print(e)
            raise

    # async def create_dataset(self, name: str, description: Optional[str] = None) -> Dict[str, Any]:
    #     """创建数据集"""
    #     payload = {"name": name, "description": description}
    #     try:
    #         resp = await self.client.post("/datasets", json=payload)
    #         return resp.get("data", {})
    #     except RAGFlowError as e:
    #         raise

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

    async def close(self):
        await self.client.close()


ragflow_service = RAGFlowService(
    settings.ragflow.origin_url,
    settings.ragflow.api_key
)
