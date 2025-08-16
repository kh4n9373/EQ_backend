from fastapi import APIRouter

from app.schemas.responses import SuccessResponse
from app.schemas.topics import TopicCreate, TopicOut, TopicUpdate
from app.services.situation_service import SituationService
from app.services.topic_service import TopicService

router = APIRouter()
topic_service = TopicService()
situation_service = SituationService()


@router.get("/")
def list_topics():
    """
    List all topics.
    """
    result = topic_service.list_topics()
    return SuccessResponse(message="Topics retrieved successfully", data=result)


@router.get("/{topic_id}")
def get_topic(topic_id: int):
    """
    Get topic by ID.
    """
    result = topic_service.get_topic(topic_id)
    return SuccessResponse(message="Topic retrieved successfully", data=result)


@router.post("/")
def create_topic(topic_in: TopicCreate):
    """
    Create new topic.
    """
    result = topic_service.create_topic(topic_in)
    return SuccessResponse(message="Topic created successfully", data=result)


@router.put("/{topic_id}")
def update_topic(topic_id: int, topic_in: TopicUpdate):
    """
    Update topic.
    """
    result = topic_service.update_topic(topic_id, topic_in)
    return SuccessResponse(message="Topic updated successfully", data=result)


@router.delete("/{topic_id}")
def delete_topic(topic_id: int):
    """
    Delete topic.
    """
    topic_service.delete_topic(topic_id)
    return SuccessResponse(message="Topic deleted successfully")


@router.get("/{topic_id}/situations")
def get_situations_by_topic(topic_id: int):
    """
    Get situations by topic ID.
    """
    result = situation_service.get_situations_by_topic(topic_id)
    return SuccessResponse(message="Situations retrieved successfully", data=result)
