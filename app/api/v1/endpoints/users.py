from fastapi import APIRouter, Depends, Query

from app.api.v1.deps import get_current_user_dep
from app.core.security import get_current_user
from app.schemas.responses import SuccessResponse
from app.schemas.users import UserProfileOut, UserShortOut
from app.services.user_service import UserService

router = APIRouter()
user_service = UserService()


@router.get("/")
def list_users(
    search: str = Query(None, min_length=2),
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    current_user: dict = get_current_user_dep,
):
    """
    List users with optional search and pagination.
    """
    users = user_service.list_users(search=search, page=page, size=size)
    return SuccessResponse(message="Users retrieved successfully", data=users)


@router.get("/me")
async def read_current_user(current_user: dict = get_current_user_dep):
    """
    Get current user info.
    """
    return SuccessResponse(
        message="Current user retrieved successfully",
        data={
            "id": (
                current_user["id"]
                if isinstance(current_user, dict)
                else getattr(current_user, "id", None)
            ),
            "email": (
                current_user["email"]
                if isinstance(current_user, dict)
                else getattr(current_user, "email", None)
            ),
            "name": (
                current_user["name"]
                if isinstance(current_user, dict)
                else getattr(current_user, "name", None)
            ),
            "picture": (
                current_user.get("picture")
                if isinstance(current_user, dict)
                else getattr(current_user, "picture", None)
            ),
        },
    )


@router.get("/search")
def search_users(
    query: str = Query(..., min_length=2), limit: int = Query(10, ge=1, le=100)
):
    """
    Search users by name.
    """
    users = user_service.search_users(query=query, limit=limit)
    return SuccessResponse(message="Users search completed successfully", data=users)


@router.get("/{user_id}")
def get_user_profile(user_id: int, current_user: dict = get_current_user_dep):
    """
    Get user profile by ID.
    """
    user = user_service.get_user_profile(user_id=user_id)
    return SuccessResponse(message="User profile retrieved successfully", data=user)
