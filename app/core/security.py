from datetime import datetime, timedelta

from authlib.integrations.starlette_client import OAuth
from fastapi import HTTPException, Request
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt

from app.core.config import settings
from app.services.user_service import UserService

oauth = OAuth()
oauth.register(
    name="google",
    server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
    client_id=settings.google_client_id,
    client_secret=settings.google_client_secret,
    client_kwargs={
        "scope": "openid email profile",
        "access_type": "offline",
        "prompt": "consent",
    },
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, settings.secret_key, algorithm=settings.algorithm
    )
    return encoded_jwt


def get_current_user(request: Request):
    token = request.cookies.get("access_token")
    if not token:
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.lower().startswith("bearer "):
            token = auth_header.split(" ", 1)[1].strip()
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    try:
        payload = jwt.decode(
            token, settings.secret_key, algorithms=[settings.algorithm]
        )
        email: str = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=401, detail="Invalid token")

        user_service = UserService()
        user = user_service.get_user_by_email(email)
        if user is None:
            raise HTTPException(status_code=401, detail="User not found")

        return {
            "id": user.id,
            "email": user.email,
            "name": user.name,
            "picture": user.picture,
        }
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")


def get_current_user_optional(request: Request):
    token = request.cookies.get("access_token")
    if not token:
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.lower().startswith("bearer "):
            token = auth_header.split(" ", 1)[1].strip()
    if not token:
        return None
    try:
        payload = jwt.decode(
            token, settings.secret_key, algorithms=[settings.algorithm]
        )
        email: str = payload.get("sub")
        if email is None:
            return None

        user_service = UserService()
        user = user_service.get_user_by_email(email)
        if user is None:
            return None

        return {
            "id": user.id,
            "email": user.email,
            "name": user.name,
            "picture": user.picture,
        }
    except JWTError:
        return None


def encrypt_refresh_token(refresh_token: str):
    return jwt.encode(
        {"refresh_token": refresh_token},
        settings.secret_key,
        algorithm=settings.algorithm,
    )


def decrypt_refresh_token(encrypted_token: str):
    payload = jwt.decode(
        encrypted_token, settings.secret_key, algorithms=[settings.algorithm]
    )
    return payload.get("refresh_token")


def get_new_access_token(user_id: int):
    user_service = UserService()
    user = user_service.get_user_by_id(user_id)
    if not user or not user.encrypted_refresh_token:
        return None

    encrypted_refresh_token = user.encrypted_refresh_token
    refresh_token = decrypt_refresh_token(encrypted_refresh_token)

    client_metadata = oauth.google.server_metadata()
    client = oauth.google._get_oauth_client(
        **client_metadata,
        token_endpoint=client_metadata["token_endpoint"],
    )
    try:
        new_token = client.refresh_token(refresh_token)
        print("successfully generate new access token")
        return new_token["access_token"]
    except Exception as e:
        print(f"Error generating new access token: {e} (refresh token expired)")
        user_service.update_user(user_id, {"encrypted_refresh_token": None})
        return None
