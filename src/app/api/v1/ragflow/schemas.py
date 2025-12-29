from typing import Optional, List

from pydantic import BaseModel, constr, Field

NonEmptyStr = constr(min_length=1, strip_whitespace=True)


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


class UploadDocumentResponse(BaseModel):
    """
    上传后的返回
    """
    id: str
    name: str
    location: str
    run: str
    size: int
    suffix: str


class HandleDocumentsResponse(BaseModel):
    """
    删除，解析等
    """
    code: int


class HandleDocumentsRequest(BaseModel):
    document_ids: List[NonEmptyStr] = Field(..., min_length=1)


class HandleChunksRequest(BaseModel):
    chunks_ids: Optional[List[NonEmptyStr]] = Field([], min_length=1)
