import pytest
from sqlalchemy.orm import Session

from app.models import User
from app.repositories.base import BaseRepository


class TestBaseRepository:
    def test_base_repository_create(self, db_session: Session, unique_user_data):
        """Test base repository create method"""
        repo = BaseRepository(User)

        # Create user with unique data
        user = repo.create(db_session, unique_user_data)

        assert user.id is not None
        assert user.email == unique_user_data["email"]
        assert user.name == unique_user_data["name"]

    def test_base_repository_get(self, db_session: Session, unique_user_data):
        """Test base repository get method"""
        repo = BaseRepository(User)

        # Create user with unique data
        user = repo.create(db_session, unique_user_data)

        # Test getting by ID
        retrieved_user = repo.get(db_session, user.id)
        assert retrieved_user is not None
        assert retrieved_user.id == user.id
        assert retrieved_user.email == unique_user_data["email"]

    def test_base_repository_get_multi(self, db_session: Session, unique_user_data):
        """Test base repository get_multi method"""
        repo = BaseRepository(User)

        # Create multiple users with unique data
        user1_data = unique_user_data.copy()
        user1_data["email"] = f"user1_{unique_user_data['email']}"
        user1_data["google_id"] = f"google1_{unique_user_data['google_id']}"

        user2_data = unique_user_data.copy()
        user2_data["email"] = f"user2_{unique_user_data['email']}"
        user2_data["google_id"] = f"google2_{unique_user_data['google_id']}"

        user1 = repo.create(db_session, user1_data)
        user2 = repo.create(db_session, user2_data)

        # Test getting multiple
        users = repo.get_multi(db_session)
        assert len(users) >= 2
        user_ids = [user.id for user in users]
        assert user1.id in user_ids
        assert user2.id in user_ids

    def test_base_repository_update(self, db_session: Session, unique_user_data):
        """Test base repository update method"""
        repo = BaseRepository(User)

        # Create user with unique data
        user = repo.create(db_session, unique_user_data)

        # Update user
        update_data = {"name": "Updated Name", "bio": "Updated bio"}
        updated_user = repo.update(db_session, user, update_data)

        assert updated_user.name == "Updated Name"
        assert updated_user.bio == "Updated bio"

    def test_base_repository_delete(self, db_session: Session, unique_user_data):
        """Test base repository delete method"""
        repo = BaseRepository(User)

        # Create user with unique data
        user = repo.create(db_session, unique_user_data)
        user_id = user.id

        # Delete user
        deleted_user = repo.delete(db_session, user_id)

        assert deleted_user.id == user_id

        # Verify user is deleted
        retrieved_user = repo.get(db_session, user_id)
        assert retrieved_user is None

    def test_base_repository_get_not_found(self, db_session: Session):
        """Test base repository get method with non-existent ID"""
        repo = BaseRepository(User)

        # Test getting non-existent user
        retrieved_user = repo.get(db_session, 99999)
        assert retrieved_user is None
