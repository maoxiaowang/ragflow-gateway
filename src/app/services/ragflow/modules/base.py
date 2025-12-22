class AsyncBase:
    def __init__(self, rag, res_dict: dict):
        self.rag = rag
        self._update_from_dict(res_dict)

    def _update_from_dict(self, res_dict: dict):
        for k, v in res_dict.items():
            if isinstance(v, dict):
                self.__dict__[k] = AsyncBase(self.rag, v)
            else:
                self.__dict__[k] = v

    def to_json(self):
        data = {}
        for name, value in self.__dict__.items():
            if name == "rag":
                continue
            if isinstance(value, AsyncBase):
                data[name] = value.to_json()
            else:
                data[name] = value
        return data

    # ===== async http wrappers =====

    async def post(self, path: str, json=None, files=None):
        return await self.rag.http.post(path, json=json, files=files)

    async def get(self, path: str, params=None):
        return await self.rag.http.get(path, params=params)

    async def put(self, path: str, json=None):
        return await self.rag.http.put(path, json=json)

    async def rm(self, path: str, json=None):
        return await self.rag.http.delete(path, json=json)

    def __str__(self):
        return str(self.to_json())
