from .base import AsyncBase

class Session(AsyncBase):
    def __init__(self, rag, res_dict):
        self.id = ""
        self.name = ""
        super().__init__(rag, res_dict)

    async def delete(self):
        res = await self.rm(f"/sessions/{self.id}", {})
        if res.get("code") != 0:
            raise RuntimeError(res["message"])
