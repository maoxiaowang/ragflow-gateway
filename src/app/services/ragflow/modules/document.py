import json
from .base import AsyncBase
from .chunk import Chunk
from ..exceptions import ResponseError


class Document(AsyncBase):
    class ParserConfig(AsyncBase):
        def __init__(self, rag, res_dict):
            super().__init__(rag, res_dict)

    def __init__(self, rag, res_dict):
        self.id = ""
        self.name = ""
        self.thumbnail = None
        self.dataset_id = None
        self.chunk_method = "naive"
        self.parser_config = {"pages": [[1, 1000000]]}
        self.source_type = "local"
        self.type = ""
        self.created_by = ""
        self.size = 0
        self.token_count = 0
        self.chunk_count = 0
        self.progress = 0.0
        self.progress_msg = ""
        self.process_begin_at = None
        self.process_duration = 0.0
        self.run = "0"
        self.status = "1"
        self.meta_fields = {}
        # 清理无效 key
        for k in list(res_dict.keys()):
            if k not in self.__dict__:
                res_dict.pop(k)
        super().__init__(rag, res_dict)

    # ===== Document operations =====
    async def update(self, update_message: dict):
        if "meta_fields" in update_message and not isinstance(update_message["meta_fields"], dict):
            raise ResponseError("meta_fields must be a dictionary")
        res = await self.put(f"/datasets/{self.dataset_id}/documents/{self.id}", update_message)
        if res.get("code") != 0:
            raise ResponseError(res.get("message"), res.get("code"))
        self._update_from_dict(res.get("data", {}))
        return self

    async def download(self):
        res = await self.get(f"/datasets/{self.dataset_id}/documents/{self.id}")
        # 如果返回 JSON 且包含 code/message，则认为是错误
        try:
            data = res.json()
            if "code" in data and "message" in data:
                raise ResponseError(data.get("message"), data.get("code"))
        except json.JSONDecodeError:
            pass
        return res.content

    async def list_chunks(self, page=1, page_size=30, keywords="", id=""):
        params = {"keywords": keywords, "page": page, "page_size": page_size, "id": id}
        res = await self.get(f"/datasets/{self.dataset_id}/documents/{self.id}/chunks", params)
        if res.get("code") == 0:
            return [Chunk(self.rag, d) for d in res["data"].get("chunks", [])]
        raise ResponseError(res.get("message"), res.get("code"))

    async def add_chunk(self, content: str, important_keywords: list[str] = [], questions: list[str] = []):
        payload = {"content": content, "important_keywords": important_keywords, "questions": questions}
        res = await self.post(f"/datasets/{self.dataset_id}/documents/{self.id}/chunks", payload)
        if res.get("code") == 0:
            return Chunk(self.rag, res["data"].get("chunk"))
        raise ResponseError(res.get("message"), res.get("code"))

    async def delete_chunks(self, ids: list[str] | None = None):
        res = await self.rm(f"/datasets/{self.dataset_id}/documents/{self.id}/chunks", {"chunk_ids": ids})
        if res.get("code") != 0:
            raise ResponseError(res.get("message"), res.get("code"))
