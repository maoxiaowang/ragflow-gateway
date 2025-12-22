class RagflowService:
    def __init__(self, client):
        self.client = client

    async def create_chat_session(self, chat_id: str):
        chat = await self.client.get_chat(chat_id)
        return await chat.create_session()
