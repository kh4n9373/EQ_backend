from fastapi import APIRouter, Depends

from app.api.v1.deps import get_current_user_dep
from app.core.metrics import (
    increment_comments_created,
    increment_reactions,
    increment_situations_created,
)
from app.core.security import get_current_user, get_current_user_optional
from app.schemas.comments import CommentCreate
from app.schemas.responses import SuccessResponse
from app.schemas.situations import (
    SituationBase,
    SituationContributeOut,
    SituationOut,
    SituationUpdate,
)
from app.services.comment_service import CommentService
from app.services.reaction_service import ReactionService
from app.services.situation_service import SituationService

router = APIRouter()
situation_service = SituationService()
comment_service = CommentService()
reaction_service = ReactionService()


@router.get("/contributed")
def get_contributed_situations(current_user: dict = get_current_user_dep):
    """
    Get all contributed situations.
    """
    result = situation_service.get_contributed_situations()
    return SuccessResponse(
        message="Contributed situations retrieved successfully", data=result
    )


@router.get("/feed")
def get_situations_feed(
    page: int = 1,
    limit: int = 10,
    sort_by: str = "created_at",
    sort_order: str = "desc",
    current_user: dict = get_current_user_dep,
):
    """
    Get situations feed with comments and reactions (aggregated).
    Supports pagination and sorting.
    """
    current_user_id = current_user.get("id") if current_user else None
    result = situation_service.get_situations_feed_paginated(
        page=page,
        limit=limit,
        sort_by=sort_by,
        sort_order=sort_order,
        current_user_id=current_user_id,
    )
    return SuccessResponse(
        message="Situations feed retrieved successfully", data=result
    )


@router.get("/{situation_id}")
def get_situation(situation_id: int):
    """
    Get situation by ID.
    """
    result = situation_service.get_situation(situation_id)
    return SuccessResponse(message="Situation retrieved successfully", data=result)


@router.get("/user/me")
def get_my_situations(current_user: dict = get_current_user_dep):
    """
    Get situations created by current user.
    """
    result = situation_service.get_situations_by_user(current_user["id"])
    return SuccessResponse(
        message="User situations retrieved successfully", data=result
    )


@router.get("/user/{user_id}")
def get_user_situations(
    user_id: int, current_user: dict = Depends(get_current_user_optional)
):
    """
    Get situations created by a specific user (public endpoint).
    """
    current_user_id = current_user.get("id") if current_user else None
    result = situation_service.get_situations_by_user_with_feed(
        user_id, current_user_id
    )
    return SuccessResponse(
        message="User situations retrieved successfully", data=result
    )


@router.post("/")
def create_situation(
    situation_in: SituationBase, current_user: dict = get_current_user_dep
):
    """
    Create new situation.
    """
    result = situation_service.create_situation(
        situation_in, user_id=current_user["id"]
    )
    # Track situation creation
    increment_situations_created()
    return SuccessResponse(message="Situation created successfully", data=result)


@router.post("/contribute")
def contribute_situation(
    situation_data: dict, current_user: dict = Depends(get_current_user)
):
    """
    Contribute a new situation.
    """
    result = situation_service.contribute_situation(situation_data, current_user["id"])
    return SuccessResponse(message="Situation contributed successfully", data=result)


@router.put("/{situation_id}")
def update_situation(
    situation_id: int,
    situation_in: SituationUpdate,
    current_user: dict = get_current_user_dep,
):
    """
    Update situation.
    """
    result = situation_service.update_situation(situation_id, situation_in)
    return SuccessResponse(message="Situation updated successfully", data=result)


@router.delete("/{situation_id}")
def delete_situation(situation_id: int, current_user: dict = get_current_user_dep):
    """
    Delete situation.
    """
    situation_service.delete_situation(situation_id)
    return SuccessResponse(message="Situation deleted successfully")


# Comment routes under situations path to match tests
@router.get("/{situation_id}/comments")
def get_comments_by_situation(situation_id: int):
    result = comment_service.get_comments_by_situation(situation_id)
    return SuccessResponse(message="Comments retrieved successfully", data=result)


@router.post("/{situation_id}/comments")
def create_comment_for_situation(
    situation_id: int,
    comment_in: CommentCreate,
    current_user: dict = get_current_user_dep,
):
    # Note: situation_id comes from path; repo uses it from comment_in if needed
    payload = comment_in.model_dump()
    payload["situation_id"] = situation_id
    result = comment_service.create_comment(
        CommentCreate(**payload), current_user["id"]
    )
    # Track comment creation
    increment_comments_created()
    return SuccessResponse(message="Comment created successfully", data=result)


# Reaction routes
@router.get("/{situation_id}/reactions")
def get_reactions_by_situation(situation_id: int):
    """
    Get reactions for a situation.
    """
    result = reaction_service.get_reactions_by_situation(situation_id)
    return SuccessResponse(message="Reactions retrieved successfully", data=result)


@router.post("/{situation_id}/reactions")
def create_reaction_for_situation(
    situation_id: int,
    reaction_data: dict,
    current_user: dict = get_current_user_dep,
):
    """
    Create a reaction for a situation.
    """
    result = reaction_service.create_reaction(
        situation_id, reaction_data.get("reaction_type"), current_user["id"]
    )
    # Track reaction creation
    increment_reactions()
    return SuccessResponse(message="Reaction created successfully", data=result)


@router.delete("/{situation_id}/reactions")
def delete_reaction_for_situation(
    situation_id: int,
    reaction_data: dict,
    current_user: dict = get_current_user_dep,
):
    """
    Delete a reaction for a situation.
    """
    reaction_service.delete_reaction(
        situation_id, reaction_data.get("reaction_type"), current_user["id"]
    )
    return SuccessResponse(message="Reaction deleted successfully")
