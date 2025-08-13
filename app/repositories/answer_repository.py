import json

from app.models import Answer
from app.repositories.base import BaseRepository
from app.schemas.analysis import AnswerCreate, AnswerUpdate


class AnswerRepository(BaseRepository[Answer, AnswerCreate, AnswerUpdate]):
    def __init__(self):
        super().__init__(Answer)

    def get_by_situation(self, db, situation_id: int):
        """Get answers by situation ID."""
        return (
            db.query(self.model).filter(self.model.situation_id == situation_id).all()
        )

    def create_answer(self, db, answer_data):
        """Create answer."""
        if hasattr(answer_data, "dict"):
            answer_data_dict = answer_data.dict()
        else:
            answer_data_dict = answer_data

        db_answer = self.model(**answer_data_dict)
        db.add(db_answer)
        db.commit()
        db.refresh(db_answer)

        return db_answer

    def create_answer_with_analysis(self, db, answer_data, scores=None, reasoning=None):
        """Create answer with scores and reasoning."""
        scores_json = json.dumps(scores) if isinstance(scores, dict) else str(scores)
        reasoning_json = (
            json.dumps(reasoning) if isinstance(reasoning, dict) else str(reasoning)
        )

        if hasattr(answer_data, "dict"):
            answer_data_dict = answer_data.dict()
        else:
            answer_data_dict = answer_data

        answer_data_dict["scores"] = scores_json
        answer_data_dict["reasoning"] = reasoning_json

        db_answer = self.model(**answer_data_dict)
        db.add(db_answer)
        db.commit()
        db.refresh(db_answer)

        return db_answer

    def get_answer_by_id(self, db, answer_id: int):
        """Get answer by ID."""
        return self.get(db, answer_id)

    def list_answers(self, db):
        """List all answers."""
        return self.get_multi(db)
