import json

from app.core.database import SessionLocal
from app.core.exceptions import NotFoundError
from app.repositories.answer_repository import AnswerRepository
from app.repositories.situation_repository import SituationRepository
from app.schemas.analysis import AnswerCreate, AnswerOut, SentimentAnalysisRequest
from app.services.openai_service import OpenAIService
from app.services.sentiment_service import SentimentService


class AnalysisService:
    def __init__(self, answer_repo=None, situation_repo=None, sentiment_service=None):
        self.answer_repo = answer_repo or AnswerRepository()
        self.situation_repo = situation_repo or SituationRepository()
        self.sentiment_service = sentiment_service or SentimentService()
        self.openai_service = OpenAIService()

    def safe_json_loads(self, val):
        """Safely load JSON value."""
        if isinstance(val, dict):
            return val
        if isinstance(val, str):
            try:
                return json.loads(val)
            except Exception:
                return {}
        return {}

    def analyze_answer(self, answer: AnswerCreate):
        """Analyze answer using OpenAI EQ analysis."""
        with SessionLocal() as db:
            situation = self.situation_repo.get(db, answer.situation_id)
            if not situation:
                raise NotFoundError("Situation", answer.situation_id)

            question = situation.question

            scores, reasoning = self.openai_service.analyze_eq(
                situation.context, question, answer.answer_text
            )

            if isinstance(self.answer_repo, AnswerRepository):
                db_answer = self.answer_repo.create_answer_with_analysis(
                    db, answer, scores, reasoning
                )
            else:
                created = self.answer_repo.create_answer(db, answer, scores, reasoning)
                if isinstance(created, tuple):
                    db_answer = created[0]
                else:
                    db_answer = created

            scores_val = self.safe_json_loads(db_answer.scores)
            reasoning_val = self.safe_json_loads(db_answer.reasoning)

            return AnswerOut(
                id=db_answer.id,
                situation_id=db_answer.situation_id,
                answer_text=db_answer.answer_text,
                scores=scores_val,
                reasoning=reasoning_val,
                question=question,
                context=situation.context,
                created_at=db_answer.created_at,
            )

    def analyze_sentiment(self, text: SentimentAnalysisRequest):
        """Analyze sentiment of text content."""
        return self.sentiment_service.analyze_sentiment(text.content)

    def get_answers_by_situation(self, situation_id: int):
        """Get all answers for a specific situation."""
        with SessionLocal() as db:
            answers = self.answer_repo.get_by_situation(db, situation_id)
            result = []

            for answer in answers:
                scores_val = self.safe_json_loads(answer.scores)
                reasoning_val = self.safe_json_loads(answer.reasoning)

                result.append(
                    AnswerOut(
                        id=answer.id,
                        situation_id=answer.situation_id,
                        answer_text=answer.answer_text,
                        scores=scores_val,
                        reasoning=reasoning_val,
                        question=(
                            answer.situation.question if answer.situation else None
                        ),
                        context=answer.situation.context if answer.situation else None,
                        created_at=answer.created_at,
                    )
                )

            return result
