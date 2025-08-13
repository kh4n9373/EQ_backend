import pytest
from sqlalchemy.orm import Session

from app.models import User
from app.repositories.user_repository import UserRepository
from app.schemas.users import UserCreate, UserUpdate


class TestUserRepository:
    def test_get_user_by_id(self, db_session: Session, unique_user_data):
        """Test getting user by ID"""
        user_repo = UserRepository()

        # Create user with unique data
        user = user_repo.create(db_session, unique_user_data)

        # Test getting by ID
        retrieved_user = user_repo.get_user_by_id(db_session, user.id)
        assert retrieved_user is not None
        assert retrieved_user.id == user.id
        assert retrieved_user.email == unique_user_data["email"]

    def test_get_user_by_email(self, db_session: Session, unique_user_data):
        """Test getting user by email"""
        user_repo = UserRepository()

        # Create user with unique data
        user = user_repo.create(db_session, unique_user_data)

        # Test getting by email
        retrieved_user = user_repo.get_user_by_email(
            db_session, unique_user_data["email"]
        )
        assert retrieved_user is not None
        assert retrieved_user.email == unique_user_data["email"]

    def test_get_user_by_google_id(self, db_session: Session, unique_user_data):
        """Test getting user by Google ID"""
        user_repo = UserRepository()

        # Create user with unique data
        user = user_repo.create(db_session, unique_user_data)

        # Test getting by Google ID
        retrieved_user = user_repo.get_user_by_google_id(
            db_session, unique_user_data["google_id"]
        )
        assert retrieved_user is not None
        assert retrieved_user.google_id == unique_user_data["google_id"]

    def test_update_user(self, db_session: Session, unique_user_data):
        """Test updating user"""
        user_repo = UserRepository()

        # Create user with unique data
        user = user_repo.create(db_session, unique_user_data)

        # Update user
        update_data = {"name": "Updated Name", "bio": "Updated bio"}
        updated_user = user_repo.update_user(db_session, user, update_data)

        assert updated_user.name == "Updated Name"
        assert updated_user.bio == "Updated bio"

    def test_delete_user(self, db_session: Session, unique_user_data):
        """Test deleting user"""
        user_repo = UserRepository()

        # Create user with unique data
        user = user_repo.create(db_session, unique_user_data)
        user_id = user.id

        # Delete user
        user_repo.delete(db_session, user_id)

        # Verify user is deleted
        retrieved_user = user_repo.get_user_by_id(db_session, user_id)
        assert retrieved_user is None

    def test_list_users(self, db_session: Session, unique_user_data):
        """Test listing all users"""
        user_repo = UserRepository()

        # Create multiple users with unique data
        user1_data = unique_user_data.copy()
        user1_data["email"] = f"user1_{unique_user_data['email']}"
        user1_data["google_id"] = f"google1_{unique_user_data['google_id']}"

        user2_data = unique_user_data.copy()
        user2_data["email"] = f"user2_{unique_user_data['email']}"
        user2_data["google_id"] = f"google2_{unique_user_data['google_id']}"

        user1 = user_repo.create(db_session, user1_data)
        user2 = user_repo.create(db_session, user2_data)

        # List users
        users = user_repo.list_users(db_session)
        assert len(users) >= 2
        user_ids = [user.id for user in users]
        assert user1.id in user_ids
        assert user2.id in user_ids

    def test_search_users_by_name(self, db_session: Session, unique_user_data):
        """Test searching users by name"""
        user_repo = UserRepository()

        # Create user with unique data
        user = user_repo.create(db_session, unique_user_data)

        # Search by name
        search_term = unique_user_data["name"].split()[0]  # Get first word of name
        users = user_repo.search_users_by_name(db_session, search_term)

        assert len(users) >= 1
        assert any(u.id == user.id for u in users)

    def test_update_user_refresh_token(self, db_session: Session, unique_user_data):
        """Test updating user refresh token"""
        user_repo = UserRepository()

        # Create user with unique data
        user = user_repo.create(db_session, unique_user_data)

        # Update refresh token
        new_token = "new_refresh_token_123"
        updated_user = user_repo.update_user_refresh_token(
            db_session, user.id, new_token
        )

        assert updated_user.encrypted_refresh_token == new_token
