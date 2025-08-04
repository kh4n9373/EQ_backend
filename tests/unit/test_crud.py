from sqlalchemy.orm import Session

from app import crud, models, schemas


class TestCRUD:
    """Complete CRUD tests"""

    def test_get_user_by_email_not_found(self, db_session: Session):
        user = crud.get_user_by_email(db_session, "nonexistent@test.com")
        assert user is None

    def test_get_user_by_email_exists(self, db_session: Session, sample_data):
        user = sample_data["user"]
        found_user = crud.get_user_by_email(db_session, user.email)
        assert found_user is not None
        assert found_user.email == user.email
        assert found_user.id == user.id

    def test_create_user(self, db_session: Session):
        user_data = {
            "email": "newuser@test.com",
            "name": "New Test User",
            "picture": "https://example.com/avatar.jpg",
        }
        user = crud.create_user(db_session, user_data)
        assert user.email == user_data["email"]
        assert user.name == user_data["name"]
        assert user.picture == user_data["picture"]
        assert user.id is not None

    def test_update_user_refresh_token(self, db_session: Session, sample_data):
        user = sample_data["user"]
        new_refresh_token = "new_refresh_token_123"
        updated_user = crud.update_user_refresh_token(
            db_session, user.id, new_refresh_token
        )
        assert updated_user.encrypted_refresh_token == new_refresh_token

    def test_get_topics_empty(self, db_session: Session):
        topics = crud.get_topics(db_session)
        assert isinstance(topics, list)

    def test_get_situations_by_topic_empty(self, db_session: Session):
        topic = models.Topic(name="Empty Topic")
        db_session.add(topic)
        db_session.flush()
        situations = crud.get_situations_by_topic(db_session, topic.id)
        assert isinstance(situations, list)
        assert len(situations) == 0

    def test_contribute_situation(self, db_session: Session, sample_data):
        user = sample_data["user"]
        topic = sample_data["topic"]
        situation_data = schemas.SituationContribute(
            topic_id=topic.id,
            context="Test contributed situation context",
            question="What would you do in this contributed situation?",
            image_url="https://example.com/image.jpg",
        )
        situation = crud.contribute_situation(db_session, situation_data, user.id)
        assert situation.topic_id == topic.id
        assert situation.user_id == user.id
        assert situation.context == situation_data.context
        assert situation.question == situation_data.question
        assert situation.image_url == situation_data.image_url
        assert situation.is_contributed is True

    def test_get_contributed_situations(self, db_session: Session):
        situations = crud.get_contributed_situations(db_session)
        assert isinstance(situations, list)

    def test_create_answer_with_scores(self, db_session: Session, sample_data):
        situation = sample_data["situation"]
        answer_data = schemas.AnswerCreate(
            situation_id=situation.id, answer_text="Test answer with scores"
        )
        scores = {
            "self_awareness": 8,
            "empathy": 7,
            "self_regulation": 6,
            "communication": 8,
            "decision_making": 7,
        }
        reasoning = {
            "self_awareness": "Good awareness",
            "empathy": "Shows empathy",
            "self_regulation": "Basic control",
            "communication": "Good communication",
            "decision_making": "Good decisions",
        }
        answer, _ = crud.create_answer(db_session, answer_data, scores, reasoning)
        assert answer.situation_id == situation.id
        assert answer.answer_text == "Test answer with scores"

    def test_get_answers_by_situation(self, db_session: Session, sample_data):
        situation = sample_data["situation"]
        answers = crud.get_answers_by_situation(db_session, situation.id)
        assert isinstance(answers, list)

    def test_get_comments_by_situation_empty(self, db_session: Session, sample_data):
        situation = sample_data["situation"]
        comments = crud.get_comments_by_situation(db_session, situation.id)
        assert isinstance(comments, list)
        assert len(comments) == 0

    def test_create_comment_with_sentiment(self, db_session: Session, sample_data):
        situation = sample_data["situation"]
        user = sample_data["user"]
        comment_data = schemas.CommentCreate(
            situation_id=situation.id, content="Test comment with sentiment"
        )
        sentiment_data = {
            "sentiment": "positive",
            "score": 0.8,
            "warning": None,
            "suggestions": ["Great comment!"],
        }
        comment = crud.create_comment(db_session, comment_data, user.id, sentiment_data)
        assert comment.situation_id == situation.id
        assert comment.content == "Test comment with sentiment"
        assert comment.sentiment_analysis == sentiment_data

    def test_get_reactions_by_situation(self, db_session: Session, sample_data):
        situation = sample_data["situation"]
        reactions = crud.get_reactions_by_situation(db_session, situation.id)
        assert isinstance(reactions, list)

    def test_create_reaction(self, db_session: Session, sample_data):
        situation = sample_data["situation"]
        user = sample_data["user"]
        reaction_data = schemas.ReactionCreate(
            situation_id=situation.id, reaction_type="like"
        )
        reaction = crud.create_reaction(db_session, reaction_data, user.id)
        assert reaction.situation_id == situation.id
        assert reaction.user_id == user.id
        assert reaction.reaction_type == "like"

    def test_delete_reaction_exists(self, db_session: Session, sample_data):
        """Test delete reaction khi reaction tồn tại"""
        situation = sample_data["situation"]
        user = sample_data["user"]
        reaction_data = schemas.ReactionCreate(
            situation_id=situation.id, reaction_type="like"
        )
        crud.create_reaction(db_session, reaction_data, user.id)
        result = crud.delete_reaction(db_session, situation.id, user.id, "like")
        assert result is True

    def test_delete_reaction_not_exists(self, db_session: Session, sample_data):
        situation = sample_data["situation"]
        user = sample_data["user"]
        result = crud.delete_reaction(db_session, situation.id, user.id, "dislike")
        assert result is False

    def test_create_result(self, db_session: Session):
        result_data = schemas.ResultCreate(
            total_scores={
                "self_awareness": 8,
                "empathy": 7,
                "self_regulation": 6,
                "communication": 8,
                "decision_making": 7,
            }
        )
        result = crud.create_result(db_session, result_data)
        assert result.total_scores == result_data.total_scores
        assert result.id is not None
