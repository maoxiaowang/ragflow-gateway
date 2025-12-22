from .base import AsyncBase
from .session import Session
from ..exceptions import ResponseError


class Chat(AsyncBase):
    def __init__(self, rag, res_dict):
        self.id = ""
        self.name = "assistant"
        self.avatar = ""
        self.llm = Chat.LLM(rag, {})
        self.prompt = Chat.Prompt(rag, {})
        super().__init__(rag, res_dict)

    class LLM(AsyncBase):
        def __init__(self, rag, res_dict):
            self.model_name = None
            self.temperature = 0.1
            self.top_p = 0.3
            self.presence_penalty = 0.4
            self.frequency_penalty = 0.7
            self.max_tokens = 512
            super().__init__(rag, res_dict)

    class Prompt(AsyncBase):
        def __init__(self, rag, res_dict):
            self.similarity_threshold = 0.2
            self.keywords_similarity_weight = 0.7
            self.top_n = 8
            self.top_k = 1024
            self.variables = [{"key": "knowledge", "optional": True}]
            self.rerank_model = ""
            self.empty_response = None
            self.opener = "Hi! I'm your assistant. What can I do for you?"
            self.show_quote = True
            self.prompt = None
            super().__init__(rag, res_dict)

    # ===== Chat operations =====

    async def update(self, update_message: dict):
        res = await self.put(f"/chats/{self.id}", update_message)
        if res.get("code") != 0:
            raise ResponseError(res["message"], code=res.get("code"))

    async def create_session(self, name: str = "New session") -> Session:
        res = await self.post(
            f"/chats/{self.id}/sessions",
            {"name": name},
        )
        if res.get("code") == 0:
            return Session(self.rag, res["data"])
        raise ResponseError(res["message"], code=res.get("code"))

    async def list_sessions(
        self,
        page: int = 1,
        page_size: int = 30,
        orderby: str = "create_time",
        desc: bool = True,
        id: str | None = None,
        name: str | None = None,
    ):
        res = await self.get(
            f"/chats/{self.id}/sessions",
            {
                "page": page,
                "page_size": page_size,
                "orderby": orderby,
                "desc": desc,
                "id": id,
                "name": name,
            },
        )
        if res.get("code") == 0:
            return [Session(self.rag, d) for d in res["data"]]
        raise ResponseError(res["message"], code=res["code"])

    async def delete_sessions(self, ids=None):
        res = await self.rm(
            f"/chats/{self.id}/sessions",
            {"ids": ids},
        )
        if res.get("code") != 0:
            raise ResponseError(res["message"], code=res["code"])
