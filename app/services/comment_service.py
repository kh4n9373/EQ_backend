from app.core.database import SessionLocal
from app.core.exceptions import NotFoundError
from app.repositories.comment_repository import CommentRepository
from app.schemas.comments import CommentCreate, CommentOut, CommentUpdate
from app.services.sentiment_service import SentimentService


class CommentService:
    def __init__(self, repo=None, sentiment_service=None):
        self.repo = repo or CommentRepository()
        self.sentiment_service = sentiment_service or SentimentService()

    def get_comments_by_situation(self, situation_id: int):
        with SessionLocal() as db:
            comments = self.repo.get_by_situation(db, situation_id)
            results = []
            for c in comments:
                if isinstance(c, dict):
                    results.append(CommentOut(**c))
                    continue
                user_dict = None
                if getattr(c, "user", None) is not None:
                    user = c.user
                    user_dict = {
                        "id": user.id,
                        "email": getattr(user, "email", None),
                        "name": getattr(user, "name", None),
                        "picture": getattr(user, "picture", None),
                    }
                results.append(
                    CommentOut(
                        id=c.id,
                        content=c.content,
                        situation_id=c.situation_id,
                        user_id=c.user_id,
                        sentiment_analysis=getattr(c, "sentiment_analysis", None),
                        created_at=c.created_at,
                        user=user_dict,
                    )
                )
            return results

    def create_comment(self, comment_in: CommentCreate, user_id: int):
        with SessionLocal() as db:
            try:
                sentiment_result = self.sentiment_service.analyze_sentiment(
                    comment_in.content
                )
                comment = self.repo.create_with_sentiment(
                    db, comment_in.dict(), user_id, sentiment_result
                )
            except Exception:
                comment = self.repo.create_with_sentiment(
                    db, comment_in.dict(), user_id
                )
            if isinstance(comment, dict):
                return CommentOut(**comment)
            user_dict = None
            if getattr(comment, "user", None) is not None:
                user = comment.user
                user_dict = {
                    "id": user.id,
                    "email": getattr(user, "email", None),
                    "name": getattr(user, "name", None),
                    "picture": getattr(user, "picture", None),
                }
            return CommentOut(
                id=comment.id,
                content=comment.content,
                situation_id=comment.situation_id,
                user_id=comment.user_id,
                sentiment_analysis=getattr(comment, "sentiment_analysis", None),
                created_at=comment.created_at,
                user=user_dict,
            )

    def get_comment(self, comment_id: int):
        """Get comment by ID."""
        with SessionLocal() as db:
            comment = self.repo.get(db, comment_id)
            if not comment:
                raise NotFoundError("Comment", comment_id)
            if isinstance(comment, dict):
                return CommentOut(**comment)
            user_dict = None
            if getattr(comment, "user", None) is not None:
                user = comment.user
                user_dict = {
                    "id": user.id,
                    "email": getattr(user, "email", None),
                    "name": getattr(user, "name", None),
                    "picture": getattr(user, "picture", None),
                }
            return CommentOut(
                id=comment.id,
                content=comment.content,
                situation_id=comment.situation_id,
                user_id=comment.user_id,
                sentiment_analysis=getattr(comment, "sentiment_analysis", None),
                created_at=comment.created_at,
                user=user_dict,
            )

    def update_comment(self, comment_id: int, comment_in: CommentUpdate):
        """Update comment."""
        with SessionLocal() as db:
            comment = self.repo.get(db, comment_id)
            if not comment:
                raise NotFoundError("Comment", comment_id)
            updated_comment = self.repo.update(db, comment, comment_in)
            if isinstance(updated_comment, dict):
                return CommentOut(**updated_comment)
            user_dict = None
            if getattr(updated_comment, "user", None) is not None:
                user = updated_comment.user
                user_dict = {
                    "id": user.id,
                    "email": getattr(user, "email", None),
                    "name": getattr(user, "name", None),
                    "picture": getattr(user, "picture", None),
                }
            return CommentOut(
                id=updated_comment.id,
                content=updated_comment.content,
                situation_id=updated_comment.situation_id,
                user_id=updated_comment.user_id,
                sentiment_analysis=getattr(updated_comment, "sentiment_analysis", None),
                created_at=updated_comment.created_at,
                user=user_dict,
            )

    def delete_comment(self, comment_id: int):
        """Delete comment."""
        with SessionLocal() as db:
            comment = self.repo.get(db, comment_id)
            if not comment:
                raise NotFoundError("Comment", comment_id)
            self.repo.delete(db, comment_id)
            return {"message": "Comment deleted successfully"}
