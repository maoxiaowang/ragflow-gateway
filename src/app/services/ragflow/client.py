from typing import Optional, List

from app.core.settings import settings
from .exceptions import ResponseError
from .http import AsyncHTTPClient
from .modules.agent import Agent
from .modules.chat import Chat
from .modules.chunk import Chunk
from .modules.dataset import DataSet


class AsyncRAGFlow:
    def __init__(self, base_url: str = None, api_key: str = None, version="v1"):
        if not base_url:
            base_url = settings.ragflow_base_url
        if not api_key:
            api_key = settings.ragflow_api_key

        timeout = settings.ragflow_timeout_seconds
        base_url = f"{base_url}/api/{version}"
        self.http = AsyncHTTPClient(base_url, api_key=api_key, timeout=timeout)

    async def close(self):
        await self.http.close()

    # ================= Dataset =================
    async def create_dataset(
        self,
        name: str,
        avatar: Optional[str] = None,
        description: Optional[str] = None,
        embedding_model: Optional[str] = None,
        permission: str = "me",
        chunk_method: str = "naive",
        parser_config=None,
    ) -> DataSet:
        payload = {
            "name": name,
            "avatar": avatar,
            "description": description,
            "embedding_model": embedding_model,
            "permission": permission,
            "chunk_method": chunk_method,
        }
        if parser_config:
            payload["parser_config"] = parser_config.to_json()

        res = await self.http.post("/datasets", payload)
        if res["code"] == 0:
            return DataSet(self, res["data"])
        raise ResponseError(res.get("message"), code=res.get("code"))

    async def list_datasets(
        self,
        page: int = 1,
        page_size: int = 30,
        orderby: str = "create_time",
        desc: bool = True,
        id: Optional[str] = None,
        name: Optional[str] = None,
    ) -> List[DataSet]:
        params = {
            "page": page,
            "page_size": page_size,
            "orderby": orderby,
            "desc": desc,
            "id": id,
            "name": name,
        }

        res = await self.http.get("/datasets", json=params)
        if res["code"] == 0:
            return [DataSet(self, d) for d in res["data"]]
        raise ResponseError(res.get("message"), code=res.get("code"))

    async def delete_datasets(self, ids: Optional[List[str]] = None):
        res = await self.http.delete("/datasets", {"ids": ids})
        if res["code"] != 0:
            raise ResponseError(res.get("message"), code=res.get("code"))

    async def get_dataset(self, name: str) -> DataSet:
        datasets = await self.list_datasets(name=name)
        if datasets:
            return datasets[0]
        raise ResponseError(f"Dataset '{name}' not found", code=404)

    # ================= Chat =================
    async def create_chat(
        self,
        name: str,
        avatar: str = "",
        dataset_ids: Optional[List[str]] = None,
        llm: Optional[Chat.LLM] = None,
        prompt: Optional[Chat.Prompt] = None,
    ) -> Chat:
        if dataset_ids is None:
            dataset_ids = []

        if llm is None:
            llm = Chat.LLM(self, {})

        if prompt is None:
            prompt = Chat.Prompt(self, {})
            if prompt.opener is None:
                prompt.opener = "Hi! I'm your assistant. What can I do for you?"
            if prompt.prompt is None:
                prompt.prompt = (
                    "You are an intelligent assistant. Your primary function is to answer questions based strictly on the provided knowledge base."
                    "**Essential Rules:**"
                    "- Your answer must be derived **solely** from this knowledge base: `{knowledge}`."
                    "- **When information is available**: Summarize the content to give a detailed answer."
                    "- **When information is unavailable**: Your response must contain this exact sentence: 'The answer you are looking for is not found in the knowledge base!' "
                    "- **Always consider** the entire conversation history."
                )

        payload = {
            "name": name,
            "avatar": avatar,
            "dataset_ids": dataset_ids,
            "llm": llm.to_json(),
            "prompt": prompt.to_json(),
        }

        res = await self.http.post("/chats", payload)
        if res["code"] == 0:
            return Chat(self, res["data"])
        raise ResponseError(res.get("message"), code=res.get("code"))

    async def list_chats(
        self,
        page: int = 1,
        page_size: int = 30,
        orderby: str = "create_time",
        desc: bool = True,
        id: Optional[str] = None,
        name: Optional[str] = None,
    ) -> List[Chat]:
        params = {
            "page": page,
            "page_size": page_size,
            "orderby": orderby,
            "desc": desc,
            "id": id,
            "name": name,
        }
        res = await self.http.get("/chats", params)
        if res["code"] == 0:
            return [Chat(self, d) for d in res["data"]]
        raise ResponseError(res.get("message"), code=res.get("code"))

    async def delete_chats(self, ids: Optional[List[str]] = None):
        res = await self.http.delete("/chats", {"ids": ids})
        if res["code"] != 0:
            raise ResponseError(res.get("message"), code=res.get("code"))

    # ================= Retrieve =================
    async def retrieve(
        self,
        dataset_ids,
        document_ids: Optional[List[str]] = None,
        question: str = "",
        page: int = 1,
        page_size: int = 30,
        similarity_threshold: float = 0.2,
        vector_similarity_weight: float = 0.3,
        top_k: int = 1024,
        rerank_id: Optional[str] = None,
        keyword: bool = False,
        cross_languages: Optional[List[str]] = None,
        metadata_condition: Optional[dict] = None,
    ) -> List[Chunk]:
        payload = {
            "page": page,
            "page_size": page_size,
            "similarity_threshold": similarity_threshold,
            "vector_similarity_weight": vector_similarity_weight,
            "top_k": top_k,
            "rerank_id": rerank_id,
            "keyword": keyword,
            "question": question,
            "dataset_ids": dataset_ids,
            "document_ids": document_ids or [],
            "cross_languages": cross_languages,
            "metadata_condition": metadata_condition,
        }

        res = await self.http.post("/retrieval", payload)
        if res["code"] == 0:
            return [Chunk(self, c) for c in res["data"]["chunks"]]
        raise ResponseError(res.get("message"), code=res.get("code"))

    # ================= Agent =================
    async def list_agents(
        self,
        page: int = 1,
        page_size: int = 30,
        orderby: str = "update_time",
        desc: bool = True,
        id: Optional[str] = None,
        title: Optional[str] = None,
    ) -> List[Agent]:
        params = {
            "page": page,
            "page_size": page_size,
            "orderby": orderby,
            "desc": desc,
            "id": id,
            "title": title,
        }
        res = await self.http.get("/agents", params)
        if res["code"] == 0:
            return [Agent(self, d) for d in res["data"]]
        raise ResponseError(res.get("message"), code=res.get("code"))

    async def create_agent(self, title: str, dsl: dict, description: Optional[str] = None):
        payload = {"title": title, "dsl": dsl}
        if description:
            payload["description"] = description
        res = await self.http.post("/agents", payload)
        if res["code"] != 0:
            raise ResponseError(res.get("message"), code=res.get("code"))

    async def update_agent(
        self,
        agent_id: str,
        title: Optional[str] = None,
        description: Optional[str] = None,
        dsl: Optional[dict] = None,
    ):
        payload = {}
        if title:
            payload["title"] = title
        if description:
            payload["description"] = description
        if dsl:
            payload["dsl"] = dsl
        res = await self.http.put(f"/agents/{agent_id}", payload)
        if res["code"] != 0:
            raise ResponseError(res.get("message"), code=res.get("code"))

    async def delete_agent(self, agent_id: str):
        res = await self.http.delete(f"/agents/{agent_id}", {})
        if res["code"] != 0:
            raise ResponseError(res.get("message"), code=res.get("code"))
