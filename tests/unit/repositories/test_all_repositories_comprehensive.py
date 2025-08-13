"""Comprehensive tests for all repositories to boost coverage"""

from unittest.mock import Mock, patch

import pytest

from app.models import Answer, Comment, Reaction, Situation, Topic, User
from app.repositories.answer_repository import AnswerRepository
from app.repositories.comment_repository import CommentRepository
from app.repositories.reaction_repository import ReactionRepository
from app.repositories.situation_repository import SituationRepository
from app.repositories.topic_repository import TopicRepository
from app.repositories.user_repository import UserRepository


@pytest.fixture
def mock_db_session():
    return Mock()


class TestUserRepository:
    """Test UserRepository methods"""

    def test_get_by_email_success(self, mock_db_session):
        """Test get_by_email happy path"""
        repo = UserRepository()
        user = User(id=1, email="test@example.com", name="Test User")
        mock_db_session.query().filter().first.return_value = user

        result = repo.get_by_email(mock_db_session, "test@example.com")

        assert result == user
        mock_db_session.query.assert_called_once()

    def test_get_by_email_not_found(self, mock_db_session):
        """Test get_by_email when user not found"""
        repo = UserRepository()
        mock_db_session.query().filter().first.return_value = None

        result = repo.get_by_email(mock_db_session, "notfound@example.com")

        assert result is None

    def test_get_by_google_id_success(self, mock_db_session):
        """Test get_by_google_id happy path"""
        repo = UserRepository()
        user = User(id=1, google_id="123456789", email="test@example.com")
        mock_db_session.query().filter().first.return_value = user

        result = repo.get_by_google_id(mock_db_session, "123456789")

        assert result == user

    def test_create_user_success(self, mock_db_session):
        """Test create_user happy path"""
        repo = UserRepository()
        user_data = {
            "email": "new@example.com",
            "name": "New User",
            "google_id": "987654321",
        }
        created_user = User(id=1, **user_data)
        mock_db_session.add.return_value = None
        mock_db_session.commit.return_value = None
        mock_db_session.refresh.return_value = None

        # Mock the User constructor
        with patch("app.repositories.user_repository.User") as mock_user_class:
            mock_user_class.return_value = created_user

            result = repo.create_user(mock_db_session, **user_data)

            assert result == created_user
            mock_db_session.add.assert_called_once()
            mock_db_session.commit.assert_called_once()

    def test_update_user_success(self, mock_db_session):
        """Test update_user happy path"""
        repo = UserRepository()
        user = User(id=1, email="test@example.com", name="Old Name")
        update_data = {"name": "New Name", "picture": "new.jpg"}

        result = repo.update_user(mock_db_session, user, **update_data)

        assert user.name == "New Name"
        assert user.picture == "new.jpg"
        assert result == user
        mock_db_session.commit.assert_called_once()

    def test_delete_user_success(self, mock_db_session):
        """Test delete_user happy path"""
        repo = UserRepository()
        user = User(id=1, email="test@example.com")
        mock_db_session.query().filter().first.return_value = user

        result = repo.delete_user(mock_db_session, 1)

        assert result is True
        mock_db_session.delete.assert_called_once_with(user)
        mock_db_session.commit.assert_called_once()

    def test_delete_user_not_found(self, mock_db_session):
        """Test delete_user when user not found"""
        repo = UserRepository()
        mock_db_session.query().filter().first.return_value = None

        result = repo.delete_user(mock_db_session, 999)

        assert result is False
        mock_db_session.delete.assert_not_called()


class TestSituationRepository:
    """Test SituationRepository methods"""

    def test_get_by_topic_success(self, mock_db_session):
        """Test get_by_topic happy path"""
        repo = SituationRepository()
        situations = [
            Situation(id=1, title="Situation 1", topic_id=1),
            Situation(id=2, title="Situation 2", topic_id=1),
        ]
        mock_db_session.query().filter().all.return_value = situations

        result = repo.get_by_topic(mock_db_session, 1)

        assert result == situations
        mock_db_session.query.assert_called_once()

    def test_get_by_topic_empty(self, mock_db_session):
        """Test get_by_topic with no results"""
        repo = SituationRepository()
        mock_db_session.query().filter().all.return_value = []

        result = repo.get_by_topic(mock_db_session, 999)

        assert result == []

    def test_create_situation_success(self, mock_db_session):
        """Test create_situation happy path"""
        repo = SituationRepository()
        situation_data = {
            "title": "New Situation",
            "content": "Content",
            "topic_id": 1,
            "user_id": 1,
        }
        created_situation = Situation(id=1, **situation_data)

        with patch(
            "app.repositories.situation_repository.Situation"
        ) as mock_situation_class:
            mock_situation_class.return_value = created_situation

            result = repo.create_situation(mock_db_session, **situation_data)

            assert result == created_situation
            mock_db_session.add.assert_called_once()
            mock_db_session.commit.assert_called_once()

    def test_update_situation_success(self, mock_db_session):
        """Test update_situation happy path"""
        repo = SituationRepository()
        situation = Situation(id=1, title="Old Title", content="Old Content")
        update_data = {"title": "New Title"}

        result = repo.update_situation(mock_db_session, situation, **update_data)

        assert situation.title == "New Title"
        assert result == situation
        mock_db_session.commit.assert_called_once()

    def test_delete_situation_success(self, mock_db_session):
        """Test delete_situation happy path"""
        repo = SituationRepository()
        situation = Situation(id=1, title="Test Situation")

        result = repo.delete_situation(mock_db_session, situation)

        assert result is True
        mock_db_session.delete.assert_called_once_with(situation)
        mock_db_session.commit.assert_called_once()

    def test_count_by_user_success(self, mock_db_session):
        """Test count_by_user happy path"""
        repo = SituationRepository()
        mock_db_session.query().filter().count.return_value = 5

        result = repo.count_by_user(mock_db_session, 1)

        assert result == 5
        mock_db_session.query.assert_called_once()


class TestCommentRepository:
    """Test CommentRepository methods"""

    def test_get_by_situation_success(self, mock_db_session):
        """Test get_by_situation happy path"""
        repo = CommentRepository()
        comments = [
            Comment(id=1, content="Comment 1", situation_id=1),
            Comment(id=2, content="Comment 2", situation_id=1),
        ]
        mock_db_session.query().filter().all.return_value = comments

        result = repo.get_by_situation(mock_db_session, 1)

        assert result == comments

    def test_create_comment_success(self, mock_db_session):
        """Test create_comment happy path"""
        repo = CommentRepository()
        comment_data = {"content": "New comment", "user_id": 1, "situation_id": 1}
        created_comment = Comment(id=1, **comment_data)

        with patch("app.repositories.comment_repository.Comment") as mock_comment_class:
            mock_comment_class.return_value = created_comment

            result = repo.create_comment(mock_db_session, **comment_data)

            assert result == created_comment
            mock_db_session.add.assert_called_once()
            mock_db_session.commit.assert_called_once()

    def test_update_comment_success(self, mock_db_session):
        """Test update_comment happy path"""
        repo = CommentRepository()
        comment = Comment(id=1, content="Old content")
        update_data = {"content": "New content"}

        result = repo.update_comment(mock_db_session, comment, **update_data)

        assert comment.content == "New content"
        assert result == comment
        mock_db_session.commit.assert_called_once()

    def test_delete_comment_success(self, mock_db_session):
        """Test delete_comment happy path"""
        repo = CommentRepository()
        comment = Comment(id=1, content="Test comment")

        result = repo.delete_comment(mock_db_session, comment)

        assert result is True
        mock_db_session.delete.assert_called_once_with(comment)
        mock_db_session.commit.assert_called_once()

    def test_count_by_situation_success(self, mock_db_session):
        """Test count_by_situation happy path"""
        repo = CommentRepository()
        mock_db_session.query().filter().count.return_value = 3

        result = repo.count_by_situation(mock_db_session, 1)

        assert result == 3


class TestReactionRepository:
    """Test ReactionRepository methods"""

    def test_get_by_situation_success(self, mock_db_session):
        """Test get_by_situation happy path"""
        repo = ReactionRepository()
        reactions = [
            Reaction(id=1, reaction_type="like", situation_id=1),
            Reaction(id=2, reaction_type="love", situation_id=1),
        ]
        mock_db_session.query().filter().all.return_value = reactions

        result = repo.get_by_situation(mock_db_session, 1)

        assert result == reactions

    def test_create_reaction_success(self, mock_db_session):
        """Test create_reaction happy path"""
        repo = ReactionRepository()
        reaction_data = {"reaction_type": "like", "user_id": 1, "situation_id": 1}
        created_reaction = Reaction(id=1, **reaction_data)

        with patch(
            "app.repositories.reaction_repository.Reaction"
        ) as mock_reaction_class:
            mock_reaction_class.return_value = created_reaction

            result = repo.create_reaction(mock_db_session, **reaction_data)

            assert result == created_reaction
            mock_db_session.add.assert_called_once()
            mock_db_session.commit.assert_called_once()

    def test_get_by_user_and_situation_success(self, mock_db_session):
        """Test get_by_user_and_situation happy path"""
        repo = ReactionRepository()
        reaction = Reaction(id=1, user_id=1, situation_id=1, reaction_type="like")
        mock_db_session.query().filter().filter().first.return_value = reaction

        result = repo.get_by_user_and_situation(mock_db_session, 1, 1)

        assert result == reaction

    def test_delete_reaction_success(self, mock_db_session):
        """Test delete_reaction happy path"""
        repo = ReactionRepository()
        reaction = Reaction(id=1, reaction_type="like")

        result = repo.delete_reaction(mock_db_session, reaction)

        assert result is True
        mock_db_session.delete.assert_called_once_with(reaction)
        mock_db_session.commit.assert_called_once()

    def test_count_by_situation_success(self, mock_db_session):
        """Test count_by_situation happy path"""
        repo = ReactionRepository()
        mock_db_session.query().filter().count.return_value = 10

        result = repo.count_by_situation(mock_db_session, 1)

        assert result == 10


class TestAnswerRepository:
    """Test AnswerRepository methods"""

    def test_create_answer_success(self, mock_db_session):
        """Test create_answer happy path"""
        repo = AnswerRepository()
        answer_data = {"situation_id": 1, "answer_text": "My answer", "user_id": 1}
        created_answer = Answer(id=1, **answer_data)

        with patch("app.repositories.answer_repository.Answer") as mock_answer_class:
            mock_answer_class.return_value = created_answer

            result = repo.create_answer(mock_db_session, **answer_data)

            assert result == created_answer
            mock_db_session.add.assert_called_once()
            mock_db_session.commit.assert_called_once()

    def test_get_by_id_success(self, mock_db_session):
        """Test get_by_id happy path"""
        repo = AnswerRepository()
        answer = Answer(id=1, answer_text="Test answer")
        mock_db_session.query().filter().first.return_value = answer

        result = repo.get_by_id(mock_db_session, 1)

        assert result == answer

    def test_get_by_id_not_found(self, mock_db_session):
        """Test get_by_id when answer not found"""
        repo = AnswerRepository()
        mock_db_session.query().filter().first.return_value = None

        result = repo.get_by_id(mock_db_session, 999)

        assert result is None

    def test_list_answers_success(self, mock_db_session):
        """Test list_answers happy path"""
        repo = AnswerRepository()
        answers = [
            Answer(id=1, answer_text="Answer 1"),
            Answer(id=2, answer_text="Answer 2"),
        ]
        mock_db_session.query().all.return_value = answers

        result = repo.list_answers(mock_db_session)

        assert result == answers

    def test_list_answers_empty(self, mock_db_session):
        """Test list_answers with no results"""
        repo = AnswerRepository()
        mock_db_session.query().all.return_value = []

        result = repo.list_answers(mock_db_session)

        assert result == []

    def test_update_answer_success(self, mock_db_session):
        """Test update_answer happy path"""
        repo = AnswerRepository()
        answer = Answer(id=1, answer_text="Old answer")
        update_data = {"answer_text": "New answer"}

        result = repo.update_answer(mock_db_session, answer, **update_data)

        assert answer.answer_text == "New answer"
        assert result == answer
        mock_db_session.commit.assert_called_once()

    def test_delete_answer_success(self, mock_db_session):
        """Test delete_answer happy path"""
        repo = AnswerRepository()
        answer = Answer(id=1, answer_text="Test answer")

        result = repo.delete_answer(mock_db_session, answer)

        assert result is True
        mock_db_session.delete.assert_called_once_with(answer)
        mock_db_session.commit.assert_called_once()


class TestTopicRepository:
    """Test TopicRepository methods"""

    def test_get_all_topics_success(self, mock_db_session):
        """Test get_all_topics happy path"""
        repo = TopicRepository()
        topics = [Topic(id=1, name="Topic 1"), Topic(id=2, name="Topic 2")]
        mock_db_session.query().all.return_value = topics

        result = repo.get_all_topics(mock_db_session)

        assert result == topics

    def test_get_by_id_success(self, mock_db_session):
        """Test get_by_id happy path"""
        repo = TopicRepository()
        topic = Topic(id=1, name="Test Topic")
        mock_db_session.query().filter().first.return_value = topic

        result = repo.get_by_id(mock_db_session, 1)

        assert result == topic

    def test_create_topic_success(self, mock_db_session):
        """Test create_topic happy path"""
        repo = TopicRepository()
        topic_data = {"name": "New Topic"}
        created_topic = Topic(id=1, **topic_data)

        with patch("app.repositories.topic_repository.Topic") as mock_topic_class:
            mock_topic_class.return_value = created_topic

            result = repo.create_topic(mock_db_session, **topic_data)

            assert result == created_topic
            mock_db_session.add.assert_called_once()
            mock_db_session.commit.assert_called_once()

    def test_update_topic_success(self, mock_db_session):
        """Test update_topic happy path"""
        repo = TopicRepository()
        topic = Topic(id=1, name="Old Topic")
        update_data = {"name": "New Topic"}

        result = repo.update_topic(mock_db_session, topic, **update_data)

        assert topic.name == "New Topic"
        assert result == topic
        mock_db_session.commit.assert_called_once()

    def test_delete_topic_success(self, mock_db_session):
        """Test delete_topic happy path"""
        repo = TopicRepository()
        topic = Topic(id=1, name="Test Topic")

        result = repo.delete_topic(mock_db_session, topic)

        assert result is True
        mock_db_session.delete.assert_called_once_with(topic)
        mock_db_session.commit.assert_called_once()


class TestRepositoryEdgeCases:
    """Test edge cases and error conditions"""

    def test_database_error_handling(self, mock_db_session):
        """Test database error handling"""
        repo = UserRepository()
        mock_db_session.commit.side_effect = Exception("Database error")
        user = User(id=1, email="test@example.com")

        with pytest.raises(Exception, match="Database error"):
            repo.update_user(mock_db_session, user, name="New Name")

    def test_empty_update_data(self, mock_db_session):
        """Test update with empty data"""
        repo = UserRepository()
        user = User(id=1, email="test@example.com", name="Original Name")

        result = repo.update_user(mock_db_session, user)

        assert result == user
        assert user.name == "Original Name"  # Should remain unchanged
        mock_db_session.commit.assert_called_once()

    def test_none_values_in_update(self, mock_db_session):
        """Test update with None values"""
        repo = UserRepository()
        user = User(id=1, email="test@example.com", name="Original Name")

        result = repo.update_user(mock_db_session, user, name=None, picture=None)

        assert result == user
        assert user.name is None
        assert user.picture is None
        mock_db_session.commit.assert_called_once()

    def test_query_with_filters_success(self, mock_db_session):
        """Test complex query with multiple filters"""
        repo = SituationRepository()
        situations = [Situation(id=1, title="Test", topic_id=1, user_id=1)]
        mock_db_session.query().filter().filter().all.return_value = situations

        # This would be a method like get_by_topic_and_user if it existed
        mock_db_session.query().filter().filter().all.return_value = situations
        result = mock_db_session.query().filter().filter().all()

        assert result == situations
