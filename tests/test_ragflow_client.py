import sys
from pathlib import Path

import pytest
from dotenv import load_dotenv
load_dotenv()

sys.path.append(str(Path(__file__).resolve().parent.parent / "src"))
from app.services.ragflow.client import AsyncRAGFlow

# ------------------- Fixture: AsyncRAGFlow 客户端 -------------------
@pytest.fixture
async def ragflow_client():
    """提供 AsyncRAGFlow 客户端实例"""
    client = AsyncRAGFlow()
    yield client
    await client.close()

# ------------------- Fixture: 测试 Dataset -------------------
@pytest.fixture
async def test_dataset(ragflow_client):
    """创建测试用 dataset，并在测试完成后删除"""
    dataset = await ragflow_client.create_dataset(name="pytest_dataset")
    yield dataset
    await ragflow_client.delete_datasets(ids=[dataset.id])

# ------------------- Fixture: 测试 Chat -------------------
@pytest.fixture
async def test_chat(ragflow_client, test_dataset):
    """创建测试用 chat，并在测试完成后删除"""
    chat = await ragflow_client.create_chat(
        name="pytest_chat",
        dataset_ids=[test_dataset.id]
    )
    yield chat
    await ragflow_client.delete_chats(ids=[chat.id])

# =================== 测试 ===================

@pytest.mark.asyncio
async def test_create_dataset(ragflow_client):
    """测试 dataset 创建"""
    dataset = await ragflow_client.create_dataset(name="pytest_dataset_2")
    assert dataset.id is not None
    # 清理
    await ragflow_client.delete_datasets(ids=[dataset.id])

@pytest.mark.asyncio
async def test_list_datasets(ragflow_client, test_dataset):
    """测试 list_datasets 能返回刚创建的 dataset"""
    datasets = await ragflow_client.list_datasets()
    assert any(d.id == test_dataset.id for d in datasets)

@pytest.mark.asyncio
async def test_create_chat(ragflow_client, test_dataset):
    """测试 chat 创建"""
    chat = await ragflow_client.create_chat(
        name="pytest_chat_2",
        dataset_ids=[test_dataset.id]
    )
    assert chat.id is not None
    await ragflow_client.delete_chats(ids=[chat.id])

@pytest.mark.asyncio
async def test_list_chats(ragflow_client, test_chat):
    """测试 list_chats 能返回刚创建的 chat"""
    chats = await ragflow_client.list_chats()
    assert any(c.id == test_chat.id for c in chats)

@pytest.mark.asyncio
async def test_retrieve(ragflow_client, test_dataset):
    """测试检索功能"""
    chunks = await ragflow_client.retrieve(
        dataset_ids=[test_dataset.id],
        question="测试问题"
    )
    assert isinstance(chunks, list)
