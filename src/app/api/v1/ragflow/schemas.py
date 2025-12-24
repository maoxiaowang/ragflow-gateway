from typing import Optional, List

from pydantic import BaseModel


class Dataset(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    created_by: str
    create_date: str
    update_date: str
    document_count: int
    chunk_count: int
    chunk_method: Optional[str] = None
    language: Optional[str] = None
    embedding_model: Optional[str] = None
    status: Optional[str] = None
    token_num: Optional[int] = None


class DatasetList(BaseModel):
    code: int
    data: List[Dataset]
    total_datasets: int
