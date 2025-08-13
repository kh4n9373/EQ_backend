from fastapi import APIRouter, HTTPException, Request, Response

from app.core.metrics import (
    decrement_active_users,
    increment_active_users,
    mark_login_failure,
    mark_login_success,
    mark_logout,
)
from app.schemas.responses import SuccessResponse
from app.services.auth_service import AuthService

router = APIRouter()
auth_service = AuthService()


@router.get("/login/google")
async def login_google(request: Request):
    return await auth_service.login_google(request)


@router.get("/callback/google")
async def auth_callback(request: Request):
    try:
        result = await auth_service.auth_callback(request)
        # Track successful login
        increment_active_users()
        mark_login_success("google")
        return result
    except HTTPException as he:
        # Track login failure
        mark_login_failure("google")
        raise he
    except Exception as e:
        # Track login failure
        mark_login_failure("google")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/logout")
def logout(response: Response):
    """
    Handle user logout.
    """
    auth_service.logout(response)
    # Track logout
    decrement_active_users()
    mark_logout()
    return SuccessResponse(message="Logged out successfully")
