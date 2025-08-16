from fastapi import APIRouter, Depends

from app.api.v1.deps import get_current_user_dep
from app.core.metrics import increment_comments_created
from app.core.security import get_current_user
from app.schemas.comments import CommentCreate, CommentOut, CommentUpdate
from app.schemas.responses import SuccessResponse
from app.services.comment_service import CommentService

router = APIRouter()
comment_service = CommentService()


@router.get("/situations/{situation_id}/comments")
def get_comments_by_situation(situation_id: int):
    """
    Get comments by situation ID.
    """
    result = comment_service.get_comments_by_situation(situation_id)
    return SuccessResponse(message="Comments retrieved successfully", data=result)


@router.post("/situations/{situation_id}/comments")
def create_comment_for_situation(
    situation_id: int,
    comment_in: CommentCreate,
    current_user: dict = get_current_user_dep,
):
    """
    Create a comment for a specific situation (path param version to match frontend).
    Ensures the `situation_id` is set from the URL if not provided in the body.
    """
    # Ensure situation_id is set on the payload
    payload = comment_in.dict()
    payload["situation_id"] = situation_id
    result = comment_service.create_comment(
        comment_in=CommentCreate(**payload),
        user_id=current_user["id"],
    )
    increment_comments_created()
    return SuccessResponse(message="Comment created successfully", data=result)


@router.post("/situations/comments")
def create_comment(
    # situation_id: int,
    comment_in: CommentCreate,
    current_user: dict = get_current_user_dep,
):
    result = comment_service.create_comment(
        comment_in=comment_in, user_id=current_user["id"]
    )
    increment_comments_created()
    return SuccessResponse(message="Comment created successfully", data=result)


@router.get("/{comment_id}")
def get_comment(comment_id: int):
    result = comment_service.get_comment(comment_id)
    return SuccessResponse(message="Comment retrieved successfully", data=result)


@router.put("/{comment_id}")
def update_comment(
    comment_id: int,
    comment_in: CommentUpdate,
    current_user: dict = get_current_user_dep,
):
    """
    Update comment.
    """
    result = comment_service.update_comment(comment_id, comment_in)
    return SuccessResponse(message="Comment updated successfully", data=result)


@router.delete("/{comment_id}")
def delete_comment(comment_id: int, current_user: dict = get_current_user_dep):
    """
    Delete comment.
    """
    comment_service.delete_comment(comment_id)
    return SuccessResponse(message="Comment deleted successfully")
