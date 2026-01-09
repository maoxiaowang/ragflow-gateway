from typing import Optional, List

from fastapi import APIRouter, Query, Depends, UploadFile, File
from fastapi.responses import StreamingResponse

from app.api.v1.ragflow.schemas import HandleDocumentsRequest
from ragflow_async_sdk.models import Dataset, Document
from ragflow_async_sdk import AsyncRAGFlowClient
from app.api.v1.ragflow.utils import get_content_disposition
from app.core.security import login_required
from app.core.settings import settings
from app.schemas import Response, PageData
from ragflow_async_sdk.utils.files import file_from_bytes


client = AsyncRAGFlowClient(
    server_url=settings.ragflow.origin_url,
    api_key=settings.ragflow.api_key,
)

router = APIRouter(prefix="/ragflow", tags=["ragflow"], dependencies=[Depends(login_required)])


@router.get("/datasets", response_model=Response[PageData[Dataset]])
async def list_datasets(
        page: Optional[int] = Query(1, ge=1),
        page_size: Optional[int] = Query(30, ge=1, le=100),
        order_by: Optional[str] = Query(None),
        desc: Optional[bool] = Query(None),
        _id: Optional[str] = Query(None),
        name: Optional[str] = Query(None),
):
    datasets, total = await client.datasets.list_datasets(
        page=page,
        page_size=page_size,
        order_by=order_by,
        desc=desc,
        dataset_id=_id,
        name=name
    )
    page_data = PageData(
        total=total,
        page=page,
        page_size=page_size,
        items=datasets
    )
    return Response(data=page_data)


@router.get("/datasets/{dataset_id}/documents", response_model=Response[PageData[Document]])
async def list_documents(
        dataset_id: str,
        page: Optional[int] = Query(1, ge=1),
        page_size: Optional[int] = Query(30, ge=1, le=100),
        order_by: Optional[str] | None = Query(None),
        desc: Optional[bool] = Query(None),
        keywords: Optional[str] = Query(None),
        suffix: Optional[str] = Query(None),
):
    items, total = await client.documents.list_documents(
        dataset_id,
        page=page,
        page_size=page_size,
        order_by=order_by,
        desc=desc,
        keywords=keywords,
        suffix=suffix
    )
    page_data = PageData(
        total=total,
        page=page,
        page_size=page_size,
        items=items
    )
    return Response(data=page_data)


@router.post("/datasets/{dataset_id}/documents",
             response_model=Response[List[Document]])
async def upload_documents(
        dataset_id: str,
        files: List[UploadFile] = File(...),
):
    files = [file_from_bytes(f.filename, await f.read(), f.content_type) for f in files]
    docs = await client.documents.upload_documents(dataset_id, files=files)
    return Response(data=docs)


@router.delete("/datasets/{dataset_id}/documents")
async def delete_documents(dataset_id: str, req: HandleDocumentsRequest):
    await client.documents.delete_documents(dataset_id, req.document_ids)
    return Response()


@router.delete("/datasets/{dataset_id}/documents/{document_id}/chunks")
async def delete_document_chunks(dataset_id: str, document_id: str):
    await client.chunks.delete_chunks(dataset_id, document_id)
    return Response()


@router.get("/datasets/{dataset_id}/documents/{document_id}")
async def download_document(
        dataset_id: str,
        document_id: str
):
    file = await client.documents.download_document(dataset_id, document_id)
    return StreamingResponse(
        file.stream,
        media_type=file.content_type,
        headers={
            "Content-Disposition": get_content_disposition(file.filename)
        },
    )


@router.post("/datasets/{dataset_id}/chunks")
async def parse_document_chunks(
        dataset_id: str,
        req: HandleDocumentsRequest,
):
    await client.documents.parse_documents(dataset_id, req.document_ids)
    return Response()
