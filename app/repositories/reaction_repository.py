from app.models import Reaction
from app.repositories.base import BaseRepository
from app.schemas.reactions import ReactionCreate, ReactionUpdate


class ReactionRepository(BaseRepository[Reaction, ReactionCreate, ReactionUpdate]):
    def __init__(self):
        super().__init__(Reaction)

    def get_by_situation(self, db, situation_id: int):
        """Get reactions by situation ID."""
        from app.models import User

        return (
            db.query(self.model)
            .join(User, self.model.user_id == User.id)
            .filter(self.model.situation_id == situation_id)
            .all()
        )

    def get_by_user_and_situation(self, db, user_id: int, situation_id: int):
        """Get reaction by user and situation."""
        return (
            db.query(self.model)
            .filter(
                self.model.user_id == user_id, self.model.situation_id == situation_id
            )
            .first()
        )

    def update_reaction(self, db, reaction_id: int, reaction_type: str):
        """Update reaction type."""
        reaction = db.query(self.model).filter(self.model.id == reaction_id).first()
        if reaction:
            reaction.reaction_type = reaction_type
            db.commit()
            db.refresh(reaction)
        return reaction
