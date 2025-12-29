from typing import Optional, List

from fastapi import APIRouter, Query, Depends, UploadFile, File
from fastapi.responses import StreamingResponse

from app.api.v1.ragflow.schemas import (
    Dataset, Document, UploadDocumentResponse, HandleDocumentsRequest,
    HandleDocumentsResponse
)
from app.api.v1.ragflow.utils import get_filename_from_response, get_content_disposition
from app.core.security import login_required
from app.schemas import Response, PageData
from app.services.ragflow.service import ragflow_service as service

router = APIRouter(prefix="/ragflow", tags=["ragflow"], dependencies=[Depends(login_required)])


@router.get("/datasets", response_model=Response[PageData[Dataset]])
async def list_datasets(
        page: Optional[int] = Query(1, ge=1),
        page_size: Optional[int] = Query(30, ge=1, le=100),
        order_by: Optional[str] = Query(None),
        desc: Optional[bool] = Query(None),
        _id: Optional[str] = Query(None),
):
    items, total = await service.list_datasets(
        page=page,
        page_size=page_size,
        orderby=order_by,
        desc=desc,
        id=_id,
    )
    page_data = PageData(
        total=total,
        page=page,
        page_size=page_size,
        items=items
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
    items, total = await service.list_documents(
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
             response_model=Response[List[UploadDocumentResponse]])
async def upload_documents(
        dataset_id: str,
        files: List[UploadFile] = File(...),
):
    docs, count = await service.upload_documents(dataset_id, files=files)
    return Response(data=[UploadDocumentResponse(**doc) for doc in docs])


@router.delete("/datasets/{dataset_id}/documents",
               response_model=Response[HandleDocumentsResponse])
async def delete_documents(dataset_id: str, req: HandleDocumentsRequest):
    resp = await service.delete_documents(dataset_id, req.document_ids)
    return Response(data=HandleDocumentsResponse(**resp))


@router.delete("/datasets/{dataset_id}/documents/{document_id}/chunks",
               response_model=HandleDocumentsResponse)
async def delete_document_chunks(dataset_id: str, document_id: str):
    resp = await service.delete_document_chunks(dataset_id, document_id)
    return Response(data=HandleDocumentsResponse(**resp))


@router.get("/datasets/{dataset_id}/documents/{document_id}")
async def download_document(
        dataset_id: str,
        document_id: str
):
    resp = await service.download_document(dataset_id, document_id)
    if resp.status_code != 200:
        return Response()
    filename = get_filename_from_response(resp)

    return StreamingResponse(
        resp.aiter_bytes(),
        media_type="application/octet-stream",
        headers={
            "Content-Disposition": get_content_disposition(filename)
        },
    )


@router.post("/datasets/{dataset_id}/chunks",
             response_model=Response[HandleDocumentsResponse])
async def parse_document_chunks(
        dataset_id: str,
        req: HandleDocumentsRequest,
):
    resp = await service.parse_document_chunks(dataset_id, req.document_ids)
    return Response(data=HandleDocumentsResponse(**resp))
