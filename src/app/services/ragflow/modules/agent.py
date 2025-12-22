from .base import AsyncBase
from .session import Session
from ..exceptions import ResponseError


class Agent(AsyncBase):
    def __init__(self, rag, res_dict):
        self.id = None
        self.avatar = None
        self.canvas_type = None
        self.description = None
        self.dsl = None
        super().__init__(rag, res_dict)

    class Dsl(AsyncBase):
        def __init__(self, rag, res_dict):
            self.answer = []
            self.components = {
                "begin": {
                    "downstream": ["Answer:China"],
                    "obj": {"component_name": "Begin", "params": {}},
                    "upstream": []
                }
            }
            self.graph = {
                "edges": [],
                "nodes": [
                    {
                        "data": {"label": "Begin", "name": "begin"},
                        "id": "begin",
                        "position": {"x": 50, "y": 200},
                        "sourcePosition": "left",
                        "targetPosition": "right",
                        "type": "beginNode"
                    }
                ]
            }
            self.history = []
            self.messages = []
            self.path = []
            self.reference = []
            super().__init__(rag, res_dict)

    # ===== Agent operations =====
    async def create_session(self, **kwargs) -> Session:
        res = await self.post(f"/agents/{self.id}/sessions", json=kwargs)
        if res.get("code") == 0:
            return Session(self.rag, res.get("data"))
        raise ResponseError(res.get("message"), res.get("code"))

    async def list_sessions(
        self,
        page: int = 1,
        page_size: int = 30,
        orderby: str = "create_time",
        desc: bool = True,
        id: str | None = None,
    ) -> list[Session]:
        params = {"page": page, "page_size": page_size, "orderby": orderby, "desc": desc, "id": id}
        res = await self.get(f"/agents/{self.id}/sessions", params)
        if res.get("code") == 0:
            return [Session(self.rag, data) for data in res.get("data", [])]
        raise ResponseError(res.get("message"), res.get("code"))

    async def delete_sessions(self, ids: list[str] | None = None):
        res = await self.rm(f"/agents/{self.id}/sessions", {"ids": ids})
        if res.get("code") != 0:
            raise ResponseError(res.get("message"), res.get("code"))
