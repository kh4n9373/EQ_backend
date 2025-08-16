import pytest
from sqlalchemy.orm import Session

from app.models import Topic
from app.repositories.topic_repository import TopicRepository


class TestTopicRepository:
    def test_create_topic(self, db_session: Session, unique_topic_data):
        """Test creating a topic"""
        topic_repo = TopicRepository()

        # Create topic with unique data
        topic = topic_repo.create(db_session, unique_topic_data)

        assert topic.id is not None
        assert topic.name == unique_topic_data["name"]

    def test_get_topic_by_id(self, db_session: Session, unique_topic_data):
        """Test getting topic by ID"""
        topic_repo = TopicRepository()

        # Create topic with unique data
        topic = topic_repo.create(db_session, unique_topic_data)

        # Test getting by ID
        retrieved_topic = topic_repo.get_topic_by_id(db_session, topic.id)
        assert retrieved_topic is not None
        assert retrieved_topic.id == topic.id
        assert retrieved_topic.name == unique_topic_data["name"]

    def test_get_topic_by_name(self, db_session: Session, unique_topic_data):
        """Test getting topic by name"""
        topic_repo = TopicRepository()

        # Create topic with unique data
        topic = topic_repo.create(db_session, unique_topic_data)

        # Test getting by name
        retrieved_topic = topic_repo.get_by_name(db_session, unique_topic_data["name"])
        assert retrieved_topic is not None
        assert retrieved_topic.name == unique_topic_data["name"]

    def test_update_topic(self, db_session: Session, unique_topic_data):
        """Test updating topic"""
        topic_repo = TopicRepository()

        # Create topic with unique data
        topic = topic_repo.create(db_session, unique_topic_data)

        # Update topic
        update_data = {"name": "Updated Topic Name"}
        updated_topic = topic_repo.update(db_session, topic, update_data)

        assert updated_topic.name == "Updated Topic Name"

    def test_delete_topic(self, db_session: Session, unique_topic_data):
        """Test deleting topic"""
        topic_repo = TopicRepository()

        # Create topic with unique data
        topic = topic_repo.create(db_session, unique_topic_data)
        topic_id = topic.id

        # Delete topic
        topic_repo.delete(db_session, topic_id)

        # Verify topic is deleted
        retrieved_topic = topic_repo.get_topic_by_id(db_session, topic_id)
        assert retrieved_topic is None

    def test_list_topics(self, db_session: Session, unique_topic_data):
        """Test listing all topics"""
        topic_repo = TopicRepository()

        # Create multiple topics with unique data
        topic1_data = unique_topic_data.copy()
        topic1_data["name"] = f"Topic1_{unique_topic_data['name']}"

        topic2_data = unique_topic_data.copy()
        topic2_data["name"] = f"Topic2_{unique_topic_data['name']}"

        topic1 = topic_repo.create(db_session, topic1_data)
        topic2 = topic_repo.create(db_session, topic2_data)

        # List topics
        topics = topic_repo.list_topics(db_session)
        assert len(topics) >= 2
        topic_ids = [topic.id for topic in topics]
        assert topic1.id in topic_ids
        assert topic2.id in topic_ids
