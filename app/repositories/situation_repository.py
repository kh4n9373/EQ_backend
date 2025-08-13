from app.models import Situation
from app.repositories.base import BaseRepository
from app.schemas.situations import SituationCreate, SituationUpdate


class SituationRepository(BaseRepository[Situation, SituationCreate, SituationUpdate]):
    def __init__(self):
        super().__init__(Situation)

    def get_by_topic(self, db, topic_id: int):
        """Get situations by topic ID."""
        return db.query(self.model).filter(self.model.topic_id == topic_id).all()

    def get_contributed_situations(self, db):
        """Get all contributed situations (with topic_id)."""
        return db.query(self.model).filter(self.model.topic_id.isnot(None)).all()

    def get_contributed_situations_with_user_info(self, db):
        """Get all contributed situations with user information."""
        from app.models import User

        return (
            db.query(self.model)
            .join(User, self.model.user_id == User.id, isouter=True)
            .filter(self.model.topic_id.isnot(None))
            .all()
        )

    def get_with_user(self, db, situation_id: int):
        """Get situation with user info."""
        return db.query(self.model).filter(self.model.id == situation_id).first()

    def create_contributed_situation(
        self, db, situation_data: dict, user_id: int | None = None
    ):
        """Create a contributed situation."""
        if user_id is not None:
            situation_data = {**situation_data, "user_id": user_id}
        db_situation = self.model(**situation_data)
        db.add(db_situation)
        db.commit()
        db.refresh(db_situation)
        return db_situation

    def get_situation_by_id(self, db, situation_id: int):
        """Get situation by ID."""
        return self.get(db, situation_id)

    def list_situations(self, db):
        """List all situations."""
        return self.get_multi(db)

    def get_by_user(self, db, user_id: int):
        """Get situations by user ID."""
        return db.query(self.model).filter(self.model.user_id == user_id).all()

    def get_by_user_with_user_info(self, db, user_id: int):
        """Get situations by user ID with user information."""
        from app.models import User

        return (
            db.query(self.model)
            .join(User, self.model.user_id == User.id)
            .filter(self.model.user_id == user_id)
            .all()
        )
