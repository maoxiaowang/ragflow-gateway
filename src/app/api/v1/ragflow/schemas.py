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


class Document(BaseModel):
    id: str
    name: str
    location: str
    chunk_count: int
    progress: float
    run: str
    size: int
    suffix: str
    type: str
    create_date: str
    create_time: int
    process_begin_at: Optional[str] = None
    process_duration: float
    status: str


class UploadDocument(BaseModel):
    """
    上传后的返回
    """
    id: str
    name: str
    location: str
    run: str
    size: int
    suffix: str