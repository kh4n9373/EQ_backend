import pytest
from sqlalchemy.orm import Session

from app.models import Comment, Situation, User
from app.repositories.comment_repository import CommentRepository
from app.repositories.situation_repository import SituationRepository
from app.repositories.topic_repository import TopicRepository
from app.repositories.user_repository import UserRepository


class TestCommentRepository:
    def test_create_comment(
        self,
        db_session: Session,
        unique_comment_data,
        unique_user_data,
        unique_situation_data,
        unique_topic_data,
    ):
        """Test creating a comment"""
        comment_repo = CommentRepository()

        # Create required dependencies first
        user_repo = UserRepository()
        situation_repo = SituationRepository()
        topic_repo = TopicRepository()

        user = user_repo.create(db_session, unique_user_data)
        topic = topic_repo.create(db_session, unique_topic_data)

        # Create situation
        situation_data = unique_situation_data.copy()
        situation_data["user_id"] = user.id
        situation_data["topic_id"] = topic.id
        situation = situation_repo.create(db_session, situation_data)

        # Update comment data with actual IDs
        comment_data = unique_comment_data.copy()
        comment_data["situation_id"] = situation.id
        comment_data["user_id"] = user.id

        # Create comment
        comment = comment_repo.create(db_session, comment_data)

        assert comment.id is not None
        assert comment.content == unique_comment_data["content"]
        assert comment.situation_id == situation.id

    def test_get_comment_by_id(
        self,
        db_session: Session,
        unique_comment_data,
        unique_user_data,
        unique_situation_data,
        unique_topic_data,
    ):
        """Test getting comment by ID"""
        comment_repo = CommentRepository()

        # Create required dependencies first
        user_repo = UserRepository()
        situation_repo = SituationRepository()
        topic_repo = TopicRepository()

        user = user_repo.create(db_session, unique_user_data)
        topic = topic_repo.create(db_session, unique_topic_data)

        # Create situation
        situation_data = unique_situation_data.copy()
        situation_data["user_id"] = user.id
        situation_data["topic_id"] = topic.id
        situation = situation_repo.create(db_session, situation_data)

        # Update comment data with actual IDs
        comment_data = unique_comment_data.copy()
        comment_data["situation_id"] = situation.id
        comment_data["user_id"] = user.id

        # Create comment
        comment = comment_repo.create(db_session, comment_data)

        # Test getting by ID
        retrieved_comment = comment_repo.get_comment_by_id(db_session, comment.id)
        assert retrieved_comment is not None
        assert retrieved_comment.id == comment.id
        assert retrieved_comment.content == unique_comment_data["content"]

    def test_get_comments_by_situation(
        self,
        db_session: Session,
        unique_comment_data,
        unique_user_data,
        unique_situation_data,
        unique_topic_data,
    ):
        """Test getting comments by situation"""
        comment_repo = CommentRepository()

        # Create required dependencies first
        user_repo = UserRepository()
        situation_repo = SituationRepository()
        topic_repo = TopicRepository()

        user = user_repo.create(db_session, unique_user_data)
        topic = topic_repo.create(db_session, unique_topic_data)

        # Create situation
        situation_data = unique_situation_data.copy()
        situation_data["user_id"] = user.id
        situation_data["topic_id"] = topic.id
        situation = situation_repo.create(db_session, situation_data)

        # Create multiple comments for the same situation
        comment1_data = unique_comment_data.copy()
        comment1_data["situation_id"] = situation.id
        comment1_data["user_id"] = user.id
        comment1_data["content"] = f"Comment1_{unique_comment_data['content']}"

        comment2_data = unique_comment_data.copy()
        comment2_data["situation_id"] = situation.id
        comment2_data["user_id"] = user.id
        comment2_data["content"] = f"Comment2_{unique_comment_data['content']}"

        comment1 = comment_repo.create(db_session, comment1_data)
        comment2 = comment_repo.create(db_session, comment2_data)

        # Test getting by situation
        comments = comment_repo.get_by_situation(db_session, situation.id)
        assert len(comments) >= 2
        comment_ids = [c.id for c in comments]
        assert comment1.id in comment_ids
        assert comment2.id in comment_ids

    def test_create_comment_with_sentiment(
        self,
        db_session: Session,
        unique_comment_data,
        unique_user_data,
        unique_situation_data,
        unique_topic_data,
    ):
        """Test creating comment with sentiment analysis"""
        comment_repo = CommentRepository()

        # Create required dependencies first
        user_repo = UserRepository()
        situation_repo = SituationRepository()
        topic_repo = TopicRepository()

        user = user_repo.create(db_session, unique_user_data)
        topic = topic_repo.create(db_session, unique_topic_data)

        # Create situation
        situation_data = unique_situation_data.copy()
        situation_data["user_id"] = user.id
        situation_data["topic_id"] = topic.id
        situation = situation_repo.create(db_session, situation_data)

        # Create comment with sentiment
        sentiment_data = {"sentiment": "positive", "score": 0.8}
        comment = comment_repo.create_with_sentiment(
            db_session, unique_comment_data, user.id, sentiment_data
        )

        assert comment.id is not None
        assert comment.sentiment_analysis == sentiment_data

    def test_update_comment(
        self,
        db_session: Session,
        unique_comment_data,
        unique_user_data,
        unique_situation_data,
        unique_topic_data,
    ):
        """Test updating comment"""
        comment_repo = CommentRepository()

        # Create required dependencies first
        user_repo = UserRepository()
        situation_repo = SituationRepository()
        topic_repo = TopicRepository()

        user = user_repo.create(db_session, unique_user_data)
        topic = topic_repo.create(db_session, unique_topic_data)

        # Create situation
        situation_data = unique_situation_data.copy()
        situation_data["user_id"] = user.id
        situation_data["topic_id"] = topic.id
        situation = situation_repo.create(db_session, situation_data)

        # Update comment data with actual IDs
        comment_data = unique_comment_data.copy()
        comment_data["situation_id"] = situation.id
        comment_data["user_id"] = user.id

        # Create comment
        comment = comment_repo.create(db_session, comment_data)

        # Update comment
        update_data = {"content": "Updated comment content"}
        updated_comment = comment_repo.update(db_session, comment, update_data)

        assert updated_comment.content == "Updated comment content"

    def test_delete_comment(
        self,
        db_session: Session,
        unique_comment_data,
        unique_user_data,
        unique_situation_data,
        unique_topic_data,
    ):
        """Test deleting comment"""
        comment_repo = CommentRepository()

        # Create required dependencies first
        user_repo = UserRepository()
        situation_repo = SituationRepository()
        topic_repo = TopicRepository()

        user = user_repo.create(db_session, unique_user_data)
        topic = topic_repo.create(db_session, unique_topic_data)

        # Create situation
        situation_data = unique_situation_data.copy()
        situation_data["user_id"] = user.id
        situation_data["topic_id"] = topic.id
        situation = situation_repo.create(db_session, situation_data)

        # Update comment data with actual IDs
        comment_data = unique_comment_data.copy()
        comment_data["situation_id"] = situation.id
        comment_data["user_id"] = user.id

        # Create comment
        comment = comment_repo.create(db_session, comment_data)
        comment_id = comment.id

        # Delete comment
        comment_repo.delete(db_session, comment_id)

        # Verify comment is deleted
        retrieved_comment = comment_repo.get_comment_by_id(db_session, comment_id)
        assert retrieved_comment is None

    def test_list_comments(
        self,
        db_session: Session,
        unique_comment_data,
        unique_user_data,
        unique_situation_data,
        unique_topic_data,
    ):
        """Test listing all comments"""
        comment_repo = CommentRepository()

        # Create required dependencies first
        user_repo = UserRepository()
        situation_repo = SituationRepository()
        topic_repo = TopicRepository()

        user = user_repo.create(db_session, unique_user_data)
        topic = topic_repo.create(db_session, unique_topic_data)

        # Create situation
        situation_data = unique_situation_data.copy()
        situation_data["user_id"] = user.id
        situation_data["topic_id"] = topic.id
        situation = situation_repo.create(db_session, situation_data)

        # Create multiple comments
        comment1_data = unique_comment_data.copy()
        comment1_data["situation_id"] = situation.id
        comment1_data["user_id"] = user.id
        comment1_data["content"] = f"Comment1_{unique_comment_data['content']}"

        comment2_data = unique_comment_data.copy()
        comment2_data["situation_id"] = situation.id
        comment2_data["user_id"] = user.id
        comment2_data["content"] = f"Comment2_{unique_comment_data['content']}"

        comment1 = comment_repo.create(db_session, comment1_data)
        comment2 = comment_repo.create(db_session, comment2_data)

        # List comments
        comments = comment_repo.list_comments(db_session)
        assert len(comments) >= 2
        comment_ids = [c.id for c in comments]
        assert comment1.id in comment_ids
        assert comment2.id in comment_ids

    def test_get_comments_by_situation_empty(
        self,
        db_session: Session,
        unique_user_data,
        unique_situation_data,
        unique_topic_data,
    ):
        """Test getting comments by situation when empty"""
        comment_repo = CommentRepository()

        # Create required dependencies first
        user_repo = UserRepository()
        situation_repo = SituationRepository()
        topic_repo = TopicRepository()

        user = user_repo.create(db_session, unique_user_data)
        topic = topic_repo.create(db_session, unique_topic_data)

        # Create situation
        situation_data = unique_situation_data.copy()
        situation_data["user_id"] = user.id
        situation_data["topic_id"] = topic.id
        situation = situation_repo.create(db_session, situation_data)

        # Test getting comments for situation with no comments
        comments = comment_repo.get_by_situation(db_session, situation.id)
        assert len(comments) == 0
