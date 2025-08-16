from app.core.database import SessionLocal
from app.models import User
from app.repositories.base import BaseRepository
from app.schemas.users import UserCreate, UserUpdate


class UserRepository(BaseRepository[User, UserCreate, UserUpdate]):
    def __init__(self):
        super().__init__(User)

    def list_users(self, db, search=None, page=1, size=10):
        """
        List users with optional search and pagination.
        """
        query = db.query(self.model)

        if search:
            query = query.filter(self.model.name.ilike(f"%{search}%"))

        # pagination
        offset = (page - 1) * size
        users = query.offset(offset).limit(size).all()

        return users

    def search_users_by_name(self, db, query: str, limit: int = 10):
        """
        Search users by name.
        """
        users = (
            db.query(self.model)
            .filter(self.model.name.ilike(f"%{query}%"))
            .limit(limit)
            .all()
        )
        return users

    def get_user_by_id(self, db, user_id: int):
        """
        Get user by ID.
        """
        return self.get(db, user_id)

    def get_user_by_email(self, db, email: str):
        """
        Get user by email.
        """
        return db.query(self.model).filter(self.model.email == email).first()

    def get_user_by_google_id(self, db, google_id: str):
        """
        Get user by Google ID.
        """
        return db.query(self.model).filter(self.model.google_id == google_id).first()

    def create_user(self, db, user_data: dict):
        """
        Create new user.
        """
        return self.create(db, user_data)

    def update_user(self, db, user: User, update_data: dict):
        """
        Update user information.
        """
        return self.update(db, user, update_data)

    def update_user_refresh_token(self, db, user_id: int, refresh_token: str):
        """
        Update user refresh token.
        """
        user = self.get(db, user_id)
        if user:
            user.encrypted_refresh_token = refresh_token
            db.commit()
            db.refresh(user)
        return user
