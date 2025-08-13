import pytest
from sqlalchemy.orm import Session

from app.models import Situation, Topic, User
from app.repositories.situation_repository import SituationRepository
from app.repositories.topic_repository import TopicRepository
from app.repositories.user_repository import UserRepository


class TestSituationRepository:
    def test_create_situation(
        self,
        db_session: Session,
        unique_situation_data,
        unique_user_data,
        unique_topic_data,
    ):
        """Test creating a situation"""
        situation_repo = SituationRepository()

        # Create required dependencies first
        user_repo = UserRepository()
        topic_repo = TopicRepository()

        user = user_repo.create(db_session, unique_user_data)
        topic = topic_repo.create(db_session, unique_topic_data)

        # Update situation data with actual IDs
        situation_data = unique_situation_data.copy()
        situation_data["user_id"] = user.id
        situation_data["topic_id"] = topic.id

        # Create situation
        situation = situation_repo.create(db_session, situation_data)

        assert situation.id is not None
        assert situation.context == unique_situation_data["context"]
        assert situation.question == unique_situation_data["question"]

    def test_get_situation_by_id(
        self,
        db_session: Session,
        unique_situation_data,
        unique_user_data,
        unique_topic_data,
    ):
        """Test getting situation by ID"""
        situation_repo = SituationRepository()

        # Create required dependencies first
        user_repo = UserRepository()
        topic_repo = TopicRepository()

        user = user_repo.create(db_session, unique_user_data)
        topic = topic_repo.create(db_session, unique_topic_data)

        # Update situation data with actual IDs
        situation_data = unique_situation_data.copy()
        situation_data["user_id"] = user.id
        situation_data["topic_id"] = topic.id

        # Create situation
        situation = situation_repo.create(db_session, situation_data)

        # Test getting by ID
        retrieved_situation = situation_repo.get_situation_by_id(
            db_session, situation.id
        )
        assert retrieved_situation is not None
        assert retrieved_situation.id == situation.id
        assert retrieved_situation.context == unique_situation_data["context"]

    def test_get_situations_by_topic(
        self,
        db_session: Session,
        unique_situation_data,
        unique_user_data,
        unique_topic_data,
    ):
        """Test getting situations by topic"""
        situation_repo = SituationRepository()

        # Create required dependencies first
        user_repo = UserRepository()
        topic_repo = TopicRepository()

        user = user_repo.create(db_session, unique_user_data)
        topic = topic_repo.create(db_session, unique_topic_data)

        # Create multiple situations for the same topic
        situation1_data = unique_situation_data.copy()
        situation1_data["user_id"] = user.id
        situation1_data["topic_id"] = topic.id
        situation1_data["context"] = f"Context1_{unique_situation_data['context']}"

        situation2_data = unique_situation_data.copy()
        situation2_data["user_id"] = user.id
        situation2_data["topic_id"] = topic.id
        situation2_data["context"] = f"Context2_{unique_situation_data['context']}"

        situation1 = situation_repo.create(db_session, situation1_data)
        situation2 = situation_repo.create(db_session, situation2_data)

        # Test getting by topic
        situations = situation_repo.get_by_topic(db_session, topic.id)
        assert len(situations) >= 2
        situation_ids = [s.id for s in situations]
        assert situation1.id in situation_ids
        assert situation2.id in situation_ids

    def test_get_contributed_situations(
        self,
        db_session: Session,
        unique_situation_data,
        unique_user_data,
        unique_topic_data,
    ):
        """Test getting contributed situations"""
        situation_repo = SituationRepository()

        # Create required dependencies first
        user_repo = UserRepository()
        topic_repo = TopicRepository()

        user = user_repo.create(db_session, unique_user_data)
        topic = topic_repo.create(db_session, unique_topic_data)

        # Create contributed situation
        situation_data = unique_situation_data.copy()
        situation_data["user_id"] = user.id
        situation_data["topic_id"] = topic.id
        situation_data["is_contributed"] = True

        situation = situation_repo.create(db_session, situation_data)

        # Test getting contributed situations
        contributed_situations = situation_repo.get_contributed_situations(db_session)
        assert len(contributed_situations) >= 1
        assert any(s.id == situation.id for s in contributed_situations)

    def test_get_situation_with_user(
        self,
        db_session: Session,
        unique_situation_data,
        unique_user_data,
        unique_topic_data,
    ):
        """Test getting situation with user relationship"""
        situation_repo = SituationRepository()

        # Create required dependencies first
        user_repo = UserRepository()
        topic_repo = TopicRepository()

        user = user_repo.create(db_session, unique_user_data)
        topic = topic_repo.create(db_session, unique_topic_data)

        # Update situation data with actual IDs
        situation_data = unique_situation_data.copy()
        situation_data["user_id"] = user.id
        situation_data["topic_id"] = topic.id

        # Create situation
        situation = situation_repo.create(db_session, situation_data)

        # Test getting with user
        retrieved_situation = situation_repo.get_with_user(db_session, situation.id)
        assert retrieved_situation is not None
        assert retrieved_situation.user_id == user.id

    def test_update_situation(
        self,
        db_session: Session,
        unique_situation_data,
        unique_user_data,
        unique_topic_data,
    ):
        """Test updating situation"""
        situation_repo = SituationRepository()

        # Create required dependencies first
        user_repo = UserRepository()
        topic_repo = TopicRepository()

        user = user_repo.create(db_session, unique_user_data)
        topic = topic_repo.create(db_session, unique_topic_data)

        # Update situation data with actual IDs
        situation_data = unique_situation_data.copy()
        situation_data["user_id"] = user.id
        situation_data["topic_id"] = topic.id

        # Create situation
        situation = situation_repo.create(db_session, situation_data)

        # Update situation
        update_data = {"context": "Updated Context", "question": "Updated Question?"}
        updated_situation = situation_repo.update(db_session, situation, update_data)

        assert updated_situation.context == "Updated Context"
        assert updated_situation.question == "Updated Question?"

    def test_delete_situation(
        self,
        db_session: Session,
        unique_situation_data,
        unique_user_data,
        unique_topic_data,
    ):
        """Test deleting situation"""
        situation_repo = SituationRepository()

        # Create required dependencies first
        user_repo = UserRepository()
        topic_repo = TopicRepository()

        user = user_repo.create(db_session, unique_user_data)
        topic = topic_repo.create(db_session, unique_topic_data)

        # Update situation data with actual IDs
        situation_data = unique_situation_data.copy()
        situation_data["user_id"] = user.id
        situation_data["topic_id"] = topic.id

        # Create situation
        situation = situation_repo.create(db_session, situation_data)
        situation_id = situation.id

        # Delete situation
        situation_repo.delete(db_session, situation_id)

        # Verify situation is deleted
        retrieved_situation = situation_repo.get_situation_by_id(
            db_session, situation_id
        )
        assert retrieved_situation is None

    def test_list_situations(
        self,
        db_session: Session,
        unique_situation_data,
        unique_user_data,
        unique_topic_data,
    ):
        """Test listing all situations"""
        situation_repo = SituationRepository()

        # Create required dependencies first
        user_repo = UserRepository()
        topic_repo = TopicRepository()

        user = user_repo.create(db_session, unique_user_data)
        topic = topic_repo.create(db_session, unique_topic_data)

        # Create multiple situations
        situation1_data = unique_situation_data.copy()
        situation1_data["user_id"] = user.id
        situation1_data["topic_id"] = topic.id
        situation1_data["context"] = f"Context1_{unique_situation_data['context']}"

        situation2_data = unique_situation_data.copy()
        situation2_data["user_id"] = user.id
        situation2_data["topic_id"] = topic.id
        situation2_data["context"] = f"Context2_{unique_situation_data['context']}"

        situation1 = situation_repo.create(db_session, situation1_data)
        situation2 = situation_repo.create(db_session, situation2_data)

        # List situations
        situations = situation_repo.list_situations(db_session)
        assert len(situations) >= 2
        situation_ids = [s.id for s in situations]
        assert situation1.id in situation_ids
        assert situation2.id in situation_ids

    def test_create_contributed_situation(
        self,
        db_session: Session,
        unique_situation_data,
        unique_user_data,
        unique_topic_data,
    ):
        """Test creating contributed situation"""
        situation_repo = SituationRepository()

        # Create required dependencies first
        user_repo = UserRepository()
        topic_repo = TopicRepository()

        user = user_repo.create(db_session, unique_user_data)
        topic = topic_repo.create(db_session, unique_topic_data)

        # Update situation data with actual IDs
        situation_data = unique_situation_data.copy()
        situation_data["user_id"] = user.id
        situation_data["topic_id"] = topic.id
        situation_data["is_contributed"] = True

        # Create contributed situation
        situation = situation_repo.create_contributed_situation(
            db_session, situation_data
        )

        assert situation.id is not None
        assert situation.is_contributed is True
        assert situation.context == unique_situation_data["context"]
