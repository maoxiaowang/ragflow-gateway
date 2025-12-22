from typing import Optional, List, Union
from .base import AsyncBase
from .document import Document


class DataSet(AsyncBase):
    # ================= Parser Config =================
    class ParserConfig(AsyncBase):
        def __init__(
            self,
            rag,
            chunk_size: int = 512,
            split_method: str = "naive",
            metadata: Optional[dict] = None,
        ):
            res_dict = {
                "chunk_size": chunk_size,
                "split_method": split_method,
                "metadata": metadata or {},
            }
            super().__init__(rag, res_dict)

    # ================= Dataset =================
    def __init__(self, rag, res_dict: dict):
        # 默认属性
        self.id: str = ""
        self.name: str = ""
        self.avatar: str = ""
        self.tenant_id: Optional[str] = None
        self.description: str = ""
        self.embedding_model: str = ""
        self.permission: str = "me"
        self.document_count: int = 0
        self.chunk_count: int = 0
        self.chunk_method: str = "naive"
        self.parser_config: Optional[DataSet.ParserConfig] = None
        self.pagerank: int = 0

        # 初始化
        super().__init__(rag, res_dict)

    # ================= Dataset CRUD =================
    async def update(self, update_message: dict) -> "DataSet":
        res = await self.put(f"/datasets/{self.id}", update_message)
        if res.get("code") != 0:
            raise RuntimeError(res.get("message"))
        self._update_from_dict(res.get("data", {}))
        return self

    # ================= Document Operations =================
    async def upload_documents(self, document_list: List[dict]) -> List[Document]:
        """
        上传文档
        document_list: [{"display_name": str, "blob": bytes|file-like}]
        """
        url = f"/datasets/{self.id}/documents"
        files = [
            ("file", (doc["display_name"], doc["blob"], "application/octet-stream"))
            for doc in document_list
        ]
        res = await self.post(url, files=files)
        if res.get("code") == 0:
            return [Document(self.rag, doc) for doc in res["data"]]
        raise RuntimeError(res.get("message"))

    async def list_documents(
        self,
        id: Optional[str] = None,
        name: Optional[str] = None,
        keywords: Optional[str] = None,
        page: int = 1,
        page_size: int = 30,
        orderby: str = "create_time",
        desc: bool = True,
        create_time_from: int = 0,
        create_time_to: int = 0,
    ) -> List[Document]:
        params = {
            "id": id,
            "name": name,
            "keywords": keywords,
            "page": page,
            "page_size": page_size,
            "orderby": orderby,
            "desc": desc,
            "create_time_from": create_time_from,
            "create_time_to": create_time_to,
        }
        res = await self.get(f"/datasets/{self.id}/documents", params=params)
        if res.get("code") == 0:
            return [Document(self.rag, d) for d in res["data"].get("docs", [])]
        raise RuntimeError(res.get("message"))

    async def delete_documents(self, ids: Optional[List[str]] = None):
        res = await self.rm(f"/datasets/{self.id}/documents", {"ids": ids})
        if res.get("code") != 0:
            raise RuntimeError(res.get("message"))

    # ================= Async Parsing =================
    async def parse_documents(self, document_ids: List[str]):
        """异步解析文档为 chunks"""
        payload = {"document_ids": document_ids}
        res = await self.post(f"/datasets/{self.id}/chunks", payload)
        if res.get("code") != 0:
            raise RuntimeError(res.get("message"))

    async def cancel_parse_documents(self, document_ids: List[str]):
        """取消文档解析任务"""
        payload = {"document_ids": document_ids}
        res = await self.rm(f"/datasets/{self.id}/chunks", payload)
        if res.get("code") != 0:
            raise RuntimeError(res.get("message"))
