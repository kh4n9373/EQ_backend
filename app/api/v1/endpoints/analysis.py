from fastapi import APIRouter, Depends

from app.api.v1.deps import get_current_user_dep
from app.schemas.analysis import AnswerCreate, AnswerOut, SentimentAnalysisRequest
from app.schemas.responses import SuccessResponse
from app.services.analysis_service import AnalysisService

router = APIRouter()
analysis_service = AnalysisService()


@router.post("/analyze")
def analyze_answer(answer: AnswerCreate, current_user: dict = get_current_user_dep):
    result = analysis_service.analyze_answer(answer)
    return SuccessResponse(message="Answer analyzed successfully", data=result)


@router.post("/analyze-sentiment")
def analyze_sentiment(
    text: SentimentAnalysisRequest, current_user: dict = get_current_user_dep
):
    result = analysis_service.analyze_sentiment(text)
    return SuccessResponse(message="Sentiment analyzed successfully", data=result)


@router.get("/situations/{situation_id}/answers")
def get_answers_by_situation(
    situation_id: int, current_user: dict = get_current_user_dep
):
    result = analysis_service.get_answers_by_situation(situation_id)
    return SuccessResponse(message="Answers retrieved successfully", data=result)
