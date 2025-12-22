from .base import AsyncBase


class ChunkUpdateError(Exception):
    def __init__(self, code=None, message=None, details=None):
        self.code = code
        self.message = message
        self.details = details
        super().__init__(message)


class Chunk(AsyncBase):
    def __init__(self, rag, res_dict):
        # ===== 基础字段 =====
        self.id = ""
        self.content = ""
        self.important_keywords = []
        self.questions = []
        self.create_time = ""
        self.create_timestamp = 0.0
        self.dataset_id = None
        self.document_name = ""
        self.document_id = ""
        self.available = True

        # ===== retrieval 结果字段 =====
        self.similarity = 0.0
        self.vector_similarity = 0.0
        self.term_similarity = 0.0
        self.positions = []
        self.doc_type = ""

        # 只保留已知字段（和官方行为一致）
        for k in list(res_dict.keys()):
            if not hasattr(self, k):
                res_dict.pop(k)

        super().__init__(rag, res_dict)

    async def update(self, update_message: dict):
        """
        更新 chunk 内容或属性
        """
        if not self.dataset_id or not self.document_id or not self.id:
            raise ChunkUpdateError(
                message="dataset_id, document_id or chunk id is missing"
            )

        res = await self.put(
            f"/datasets/{self.dataset_id}/documents/{self.document_id}/chunks/{self.id}",
            update_message,
        )

        if res.get("code") != 0:
            raise ChunkUpdateError(
                code=res.get("code"),
                message=res.get("message"),
                details=res.get("details"),
            )
