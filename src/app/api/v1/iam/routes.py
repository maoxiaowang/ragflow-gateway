from fastapi import APIRouter, Query, Depends

from app.api.v1.iam.deps import get_user_service
from app.core.security import login_required, has_role
from app.schemas import Response, PageData
from app.schemas.iam import UserOut
from app.services.iam import UserService

router = APIRouter(
    prefix="/iam",
    tags=["user"],
    dependencies=[
        Depends(login_required),
        Depends(has_role("admin"))
    ]
)


@router.get("/users", response_model=Response[PageData[UserOut]])
async def list_users(
        page: int = Query(1, ge=1),
        page_size: int = Query(10, ge=1, le=100),
        order_by: str | None = Query(None),
        desc: bool = Query(False),
        service: UserService = Depends(get_user_service)
):
    items, total = await service.get_paged(
        page=page,
        page_size=page_size,
        order_by=order_by,
        desc=desc,
    )

    page_data = PageData(
        total=total,
        page=page,
        page_size=page_size,
        items=items
    )
    return Response(data=page_data)
