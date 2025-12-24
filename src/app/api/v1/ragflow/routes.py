import asyncio

from fastapi import APIRouter, Query, Depends

from app.api.v1.ragflow.schemas import Dataset
from app.core.security import login_required
from app.schemas import Response, PageData
from app.services.ragflow.service import ragflow_service as service

router = APIRouter(prefix="/ragflow", tags=["ragflow"], dependencies=[Depends(login_required)])


@router.get("/datasets", response_model=Response[PageData[Dataset]])
async def list_datasets(
        page: int = Query(1, ge=1),
        page_size: int = Query(30, ge=1, le=100),
        order_by: str | None = Query(None),
        desc: bool = Query(True)
):
    print('start list_datasets')
    items, total = await service.list_datasets(
        page=page,
        page_size=page_size,
        order_by=order_by,
        desc=desc,
    )
    print('total items', total)

    page_data = PageData(
        total=total,
        page=page,
        page_size=page_size,
        items=items
    )
    print('page_data', page_data)
    return Response(data=page_data)
