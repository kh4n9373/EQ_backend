from datetime import datetime, timezone

from fastapi import HTTPException, Request, Response
from fastapi.responses import RedirectResponse

from app.core.config import settings
from app.core.security import create_access_token, encrypt_refresh_token, oauth
from app.services.user_service import UserService


class AuthService:
    def __init__(self, user_service=None):
        self.user_service = user_service or UserService()

    async def login_google(self, request: Request):
        redirect_uri = request.url_for("auth_callback")
        return await oauth.google.authorize_redirect(request, redirect_uri)

    async def auth_callback(self, request: Request):
        try:
            token = await oauth.google.authorize_access_token(request)
        except Exception as e:
            raise HTTPException(
                status_code=401, detail=f"Could not validate credentials, Error: {e}"
            )

        try:
            user_info = token.get("userinfo")
            if not user_info:
                raise HTTPException(
                    status_code=401, detail="Could not validate credentials"
                )

            refresh_token = token.get("refresh_token")

            existing_user = self.user_service.get_user_by_email(user_info.get("email"))

            if existing_user:
                update_data = {}
                if existing_user.name != user_info["name"]:
                    update_data["name"] = user_info["name"]
                if existing_user.picture != user_info["picture"]:
                    update_data["picture"] = user_info["picture"]

                if update_data:
                    update_data["updated_at"] = datetime.now(timezone.utc)
                    self.user_service.update_user(existing_user.id, update_data)

                user_id = existing_user.id
            else:
                new_user_data = {
                    "google_id": user_info["sub"],
                    "email": user_info["email"],
                    "name": user_info["name"],
                    "picture": user_info["picture"],
                    "encrypted_refresh_token": (
                        encrypt_refresh_token(refresh_token) if refresh_token else None
                    ),
                    "is_active": True,
                    "created_at": datetime.now(timezone.utc),
                    "updated_at": datetime.now(timezone.utc),
                }
                new_user = self.user_service.create_user(new_user_data)
                user_id = new_user.id

            if refresh_token:
                encrypted_refresh_token = encrypt_refresh_token(refresh_token)
                self.user_service.update_user_refresh_token(
                    user_id, encrypted_refresh_token
                )

            access_token = create_access_token(data={"sub": user_info["email"]})

            response = RedirectResponse(url=settings.frontend_url)
            response.set_cookie(
                key="access_token",
                value=access_token,
                httponly=True,
                samesite="lax",
                secure=True,
            )
            return response
        except HTTPException as he:
            raise he
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"User service error: {str(e)}")

    def logout(self, response: Response):
        response.delete_cookie("access_token", path="/")
        return {"message": "Logged out"}
