from typing import Optional

from pydantic import BaseModel


class LoginResponse(BaseModel):
    message: str = "Login successful"
    redirect_url: str = "http://localhost:3000/"


class LogoutResponse(BaseModel):
    message: str = "Logged out"


class AuthError(BaseModel):
    detail: str
    error_code: Optional[str] = None
