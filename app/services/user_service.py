from app.core.database import SessionLocal
from app.core.exceptions import NotFoundError
from app.repositories.user_repository import UserRepository
from app.schemas.users import UserProfileOut, UserShortOut


class UserService:
    def __init__(self, user_repo=None):
        self.user_repo = user_repo or UserRepository()

    def list_users(self, search=None, page=1, size=10):
        """
        List users with optional search and pagination.
        """
        with SessionLocal() as db:
            users = self.user_repo.list_users(db, search=search, page=page, size=size)
            return [
                UserShortOut(id=user.id, name=user.name, picture=user.picture)
                for user in users
            ]

    def search_users(self, query: str, limit: int = 10):
        """
        Search users by name.
        """
        if not query or len(query) < 2:
            return []

        with SessionLocal() as db:
            users = self.user_repo.search_users_by_name(db, query=query, limit=limit)
            return [
                UserShortOut(id=user.id, name=user.name, picture=user.picture)
                for user in users
            ]

    def get_user_profile(self, user_id: int):
        """
        Get user profile by ID.
        """
        with SessionLocal() as db:
            user = self.user_repo.get_user_by_id(db, user_id=user_id)
            if not user:
                raise NotFoundError("User", user_id)

            return UserProfileOut(
                id=user.id,
                name=user.name,
                email=user.email,
                picture=user.picture,
                bio=user.bio,
            )

    def get_user_by_email(self, email: str):
        """
        Get user by email.
        """
        with SessionLocal() as db:
            return self.user_repo.get_user_by_email(db, email=email)

    def create_user(self, user_data: dict):
        """
        Create new user.
        """
        with SessionLocal() as db:
            return self.user_repo.create_user(db, user_data=user_data)

    def update_user(self, user_id: int, update_data: dict):
        """
        Update user information.
        """
        with SessionLocal() as db:
            user = self.user_repo.get_user_by_id(db, user_id=user_id)
            if not user:
                raise NotFoundError("User", user_id)

            return self.user_repo.update_user(db, user=user, update_data=update_data)

    def update_user_refresh_token(self, user_id: int, refresh_token: str):
        """
        Update user refresh token.
        """
        with SessionLocal() as db:
            return self.user_repo.update_user_refresh_token(
                db, user_id=user_id, refresh_token=refresh_token
            )
