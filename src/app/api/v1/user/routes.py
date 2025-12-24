from fastapi import APIRouter, Query, Depends

from app.api.v1.auth.deps import get_user_service
from app.api.v1.auth.schemas import UserOut
from app.core.security import login_required
from app.schemas import Response, PageData
from app.services.auth import UserService

router = APIRouter(prefix="/users", tags=["user"], dependencies=[Depends(login_required)])


@router.get("", response_model=Response[PageData[UserOut]])
async def list_users(
        page: int = Query(1, ge=1),
        page_size: int = Query(10, ge=1, le=100),
        order_by: str | None = Query(None),
        desc_order: bool = Query(False),
        service: UserService = Depends(get_user_service)
):
    items, total = await service.get_paged(
        page=page,
        page_size=page_size,
        order_by=order_by,
        desc_order=desc_order,
    )

    page_data = PageData(
        total=total,
        page=page,
        page_size=page_size,
        items=items
    )
    return Response(data=page_data)