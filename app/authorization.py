from starlette.config import Config
from authlib.integrations.starlette_client import OAuth
from jose import jwt, JWTError
from datetime import datetime, timedelta
from fastapi import Depends, HTTPException, Request
from fastapi.security import OAuth2PasswordBearer
from starlette import status
from sqlalchemy.orm import Session
from app import crud
from authlib.oauth2.rfc6749 import OAuth2Error
from app.database import SessionLocal
config = Config(".env")
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
oauth = OAuth(config)
oauth.register(
    name='google',
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_id=config('GOOGLE_CLIENT_ID'),
    client_secret=config('GOOGLE_CLIENT_SECRET'),
    client_kwargs={
        'scope': 'openid email profile',
        'access_type': 'offline',
        'prompt': 'consent'
    }
)

SECRET_KEY = config('SECRET_KEY')
ALGORITHM = config('ALGORITHM')
ACCESS_TOKEN_EXPIRE_MINUTES = config('ACCESS_TOKEN_EXPIRE_MINUTES', cast=int)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def get_current_user(request: Request, db: Session = Depends(get_db)):
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        user = crud.get_user_by_email(db, email=email)
        if user is None:
            raise HTTPException(status_code=401, detail="User not found")
        return {
            "id": user.id,
            "email": user.email,
            "name": user.name,
            "picture": user.picture
        }
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
    
def encrypt_refresh_token(refresh_token: str):
    return jwt.encode(refresh_token, SECRET_KEY, algorithm=ALGORITHM)

def decrypt_refresh_token(encrypted_token: str):
    return jwt.decode(encrypted_token, SECRET_KEY, algorithms=[ALGORITHM])

def get_new_access_token(user_id: int, db: Session):
    user = crud.get_user_by_id(db, user_id)
    if not user or not user.encrypted_refresh_token:
        return None
    encrypted_refresh_token = user.encrypted_refresh_token
    refresh_token = decrypt_refresh_token(encrypted_refresh_token)
    
    client_metadata = oauth.google.server_metadata()
    client = oauth.google._get_oauth_client(
        **client_metadata,
        token_endpoint=client_metadata['token_endpoint'],
    )
    try:
        new_token = client.refresh_token(refresh_token)
        print("sucessfull generate new access token")
        return new_token["access_token"]
    except Oauth2Error as e:
        print(f"Error generating new access token: {e} (refresh token expired)")
        crud.update_user(db, db_user=user, data_to_update={'encrypted_refresh_token': None})
        return None
