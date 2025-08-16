from app.models import Comment
from app.repositories.base import BaseRepository
from app.schemas.comments import CommentCreate, CommentUpdate


class CommentRepository(BaseRepository[Comment, CommentCreate, CommentUpdate]):
    def __init__(self):
        super().__init__(Comment)

    def get_by_situation(self, db, situation_id: int):
        """Get comments by situation ID."""
        return (
            db.query(self.model).filter(self.model.situation_id == situation_id).all()
        )

    def create_with_sentiment(
        self, db, comment_data: dict, user_id: int, sentiment_result: dict = None
    ):
        """Create comment with sentiment analysis."""
        comment_data["user_id"] = user_id
        if sentiment_result:
            comment_data["sentiment_analysis"] = sentiment_result

        db_comment = self.model(**comment_data)
        db.add(db_comment)
        db.commit()
        db.refresh(db_comment)

        return db_comment

    def get_comment_by_id(self, db, comment_id: int):
        """Get comment by ID."""
        return self.get(db, comment_id)

    def list_comments(self, db):
        """List all comments."""
        return self.get_multi(db)
