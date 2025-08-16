import pytest
from sqlalchemy.orm import Session

from app.models import Answer, Situation, User
from app.repositories.answer_repository import AnswerRepository
from app.repositories.situation_repository import SituationRepository
from app.repositories.topic_repository import TopicRepository
from app.repositories.user_repository import UserRepository


class TestAnswerRepository:
    def test_create_answer(
        self,
        db_session: Session,
        unique_answer_data,
        unique_user_data,
        unique_situation_data,
        unique_topic_data,
    ):
        """Test creating an answer"""
        answer_repo = AnswerRepository()

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

        # Update answer data with actual IDs
        answer_data = unique_answer_data.copy()
        answer_data["situation_id"] = situation.id

        # Create answer
        answer = answer_repo.create_answer(db_session, answer_data)

        assert answer.id is not None
        assert answer.answer_text == unique_answer_data["answer_text"]
        assert answer.situation_id == situation.id

    def test_get_answer_by_id(
        self,
        db_session: Session,
        unique_answer_data,
        unique_user_data,
        unique_situation_data,
        unique_topic_data,
    ):
        """Test getting answer by ID"""
        answer_repo = AnswerRepository()

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

        # Update answer data with actual IDs
        answer_data = unique_answer_data.copy()
        answer_data["situation_id"] = situation.id

        # Create answer
        answer = answer_repo.create_answer(db_session, answer_data)

        # Test getting by ID
        retrieved_answer = answer_repo.get_answer_by_id(db_session, answer.id)
        assert retrieved_answer is not None
        assert retrieved_answer.id == answer.id
        assert retrieved_answer.answer_text == unique_answer_data["answer_text"]

    def test_get_answers_by_situation(
        self,
        db_session: Session,
        unique_answer_data,
        unique_user_data,
        unique_situation_data,
        unique_topic_data,
    ):
        """Test getting answers by situation"""
        answer_repo = AnswerRepository()

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

        # Create multiple answers for the same situation
        answer1_data = unique_answer_data.copy()
        answer1_data["situation_id"] = situation.id
        answer1_data["answer_text"] = f"Answer1_{unique_answer_data['answer_text']}"

        answer2_data = unique_answer_data.copy()
        answer2_data["situation_id"] = situation.id
        answer2_data["answer_text"] = f"Answer2_{unique_answer_data['answer_text']}"

        answer1 = answer_repo.create_answer(db_session, answer1_data)
        answer2 = answer_repo.create_answer(db_session, answer2_data)

        # Test getting by situation
        answers = answer_repo.get_by_situation(db_session, situation.id)
        assert len(answers) >= 2
        answer_ids = [a.id for a in answers]
        assert answer1.id in answer_ids
        assert answer2.id in answer_ids

    def test_create_answer_with_analysis(
        self,
        db_session: Session,
        unique_answer_data,
        unique_user_data,
        unique_situation_data,
        unique_topic_data,
    ):
        """Test creating answer with analysis"""
        answer_repo = AnswerRepository()

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

        # Create answer with analysis
        answer_data = unique_answer_data.copy()
        answer_data["situation_id"] = situation.id

        answer = answer_repo.create_answer_with_analysis(
            db_session,
            answer_data,
            scores=unique_answer_data["scores"],
            reasoning=unique_answer_data["reasoning"],
        )

        assert answer.id is not None
        # The scores and reasoning are stored as JSON strings, so we need to parse them
        import json

        assert json.loads(answer.scores) == unique_answer_data["scores"]
        assert json.loads(answer.reasoning) == unique_answer_data["reasoning"]

    def test_update_answer(
        self,
        db_session: Session,
        unique_answer_data,
        unique_user_data,
        unique_situation_data,
        unique_topic_data,
    ):
        """Test updating answer"""
        answer_repo = AnswerRepository()

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

        # Update answer data with actual IDs
        answer_data = unique_answer_data.copy()
        answer_data["situation_id"] = situation.id

        # Create answer
        answer = answer_repo.create_answer(db_session, answer_data)

        # Update answer
        update_data = {"answer_text": "Updated answer text"}
        updated_answer = answer_repo.update(db_session, answer, update_data)

        assert updated_answer.answer_text == "Updated answer text"

    def test_delete_answer(
        self,
        db_session: Session,
        unique_answer_data,
        unique_user_data,
        unique_situation_data,
        unique_topic_data,
    ):
        """Test deleting answer"""
        answer_repo = AnswerRepository()

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

        # Update answer data with actual IDs
        answer_data = unique_answer_data.copy()
        answer_data["situation_id"] = situation.id

        # Create answer
        answer = answer_repo.create_answer(db_session, answer_data)
        answer_id = answer.id

        # Delete answer
        answer_repo.delete(db_session, answer_id)

        # Verify answer is deleted
        retrieved_answer = answer_repo.get_answer_by_id(db_session, answer_id)
        assert retrieved_answer is None

    def test_list_answers(
        self,
        db_session: Session,
        unique_answer_data,
        unique_user_data,
        unique_situation_data,
        unique_topic_data,
    ):
        """Test listing all answers"""
        answer_repo = AnswerRepository()

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

        # Create multiple answers
        answer1_data = unique_answer_data.copy()
        answer1_data["situation_id"] = situation.id
        answer1_data["answer_text"] = f"Answer1_{unique_answer_data['answer_text']}"

        answer2_data = unique_answer_data.copy()
        answer2_data["situation_id"] = situation.id
        answer2_data["answer_text"] = f"Answer2_{unique_answer_data['answer_text']}"

        answer1 = answer_repo.create_answer(db_session, answer1_data)
        answer2 = answer_repo.create_answer(db_session, answer2_data)

        # List answers
        answers = answer_repo.list_answers(db_session)
        assert len(answers) >= 2
        answer_ids = [a.id for a in answers]
        assert answer1.id in answer_ids
        assert answer2.id in answer_ids

    def test_get_answers_by_situation_empty(
        self,
        db_session: Session,
        unique_user_data,
        unique_situation_data,
        unique_topic_data,
    ):
        """Test getting answers by situation when empty"""
        answer_repo = AnswerRepository()

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

        # Test getting answers for situation with no answers
        answers = answer_repo.get_by_situation(db_session, situation.id)
        assert len(answers) == 0
