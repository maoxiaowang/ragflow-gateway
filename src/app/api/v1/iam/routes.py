from typing import List

from fastapi import APIRouter, Query, Depends, Path

from app.api.v1.iam.deps import get_user_service, get_role_service
from app.api.v1.iam.schemas import AssignRolesRequest, CreateUserRequest, DisableUsersRequest
from app.core.security import login_required, has_role, get_current_user
from app.models import User
from app.schemas import Response, PageData
from app.schemas.iam import UserOut
from app.schemas.iam.role import RoleOut
from app.services.iam import UserService
from app.services.iam.role import RoleService

router = APIRouter(
    prefix="/iam",
    tags=["iam"],
    dependencies=[
        Depends(login_required),
        Depends(has_role("admin"))
    ]
)


@router.get("/users", response_model=Response[PageData[UserOut]])
async def list_users(
        page: int = Query(1, ge=1),
        page_size: int = Query(10, ge=1, le=100),
        order_by: str | None = Query("id"),
        desc: bool = Query(True),
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


@router.post("/users", response_model=Response[UserOut])
async def create_user(
        req: CreateUserRequest,
        service: UserService = Depends(get_user_service)
):
    user = await service.create_user(req)
    return Response(data=user)


@router.delete("/users/{user_id}")
async def delete_user(
    user_id: int,
    service: UserService = Depends(get_user_service),
    current_user: User = Depends(get_current_user),
):
    result = await service.delete_user(user_id, current_user.id)
    return Response(data=result)


@router.delete("/users")
async def delete_users_batch(
    user_ids: List[int],
    service: UserService = Depends(get_user_service),
    current_user: User = Depends(get_current_user),
):
    result = await service.delete_users_batch(user_ids, current_user.id)
    return Response(data=result)


@router.get("/users/{user_id}/roles", response_model=Response[List[RoleOut]])
async def list_user_roles(
        user_id: int = Path(..., ge=1),
        service: UserService = Depends(get_user_service)
):
    """
    Fetch roles for a user
    """
    roles = await service.list_roles_for_user(user_id)
    return Response(data=roles)


@router.post("/users/{user_id}/roles", response_model=Response[List[RoleOut]])
async def assign_user_roles(
        req: AssignRolesRequest,
        user_id: int = Path(..., ge=1),
        service: UserService = Depends(get_user_service)
):
    """
    Assign roles to a user
    """
    roles = await service.assign_roles(user_id, req.role_ids)
    return Response(data=roles)


@router.post("/users/disable", response_model=Response[List[UserOut]])
async def disable_users(
        req: DisableUsersRequest,
        service: UserService = Depends(get_user_service),
        user: User = Depends(get_current_user),
):
    """
    Disable or enable multiple users
    """
    users = await service.disable_users(req.user_ids, user.id, req.disable)
    return Response(data=users)


@router.get("/roles", response_model=Response[PageData[RoleOut]])
async def list_roles(
        page: int = Query(1, ge=1),
        page_size: int = Query(10, ge=1, le=100),
        order_by: str | None = Query("id"),
        desc: bool = Query(True),
        service: RoleService = Depends(get_role_service)
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
