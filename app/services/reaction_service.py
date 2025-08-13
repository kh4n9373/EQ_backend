from app.core.database import SessionLocal
from app.repositories.reaction_repository import ReactionRepository
from app.schemas.reactions import ReactionOut


class ReactionService:
    def __init__(self):
        self.repo = ReactionRepository()

    def get_reactions_by_situation(self, situation_id: int):
        """Get reactions by situation ID."""
        with SessionLocal() as db:
            reactions = self.repo.get_by_situation(db, situation_id)
            result = []
            for reaction in reactions:
                user_dict = None
                if hasattr(reaction, "user") and reaction.user:
                    user_dict = {
                        "id": reaction.user.id,
                        "name": reaction.user.name,
                        "picture": reaction.user.picture,
                    }
                result.append(
                    ReactionOut(
                        id=reaction.id,
                        situation_id=reaction.situation_id,
                        user_id=reaction.user_id,
                        reaction_type=reaction.reaction_type,
                        created_at=reaction.created_at,
                        user=user_dict,
                    )
                )
            return result

    def create_reaction(self, situation_id: int, reaction_type: str, user_id: int):
        """Create a reaction."""
        with SessionLocal() as db:
            existing_reaction = self.repo.get_by_user_and_situation(
                db, user_id, situation_id
            )
            if existing_reaction:
                reaction = self.repo.update_reaction(
                    db, existing_reaction.id, reaction_type
                )
            else:
                reaction_data = {
                    "situation_id": situation_id,
                    "user_id": user_id,
                    "reaction_type": reaction_type,
                }
                reaction = self.repo.create(db, reaction_data)

            user_dict = None
            if hasattr(reaction, "user") and reaction.user:
                user_dict = {
                    "id": reaction.user.id,
                    "name": reaction.user.name,
                    "picture": reaction.user.picture,
                }

            return ReactionOut(
                id=reaction.id,
                situation_id=reaction.situation_id,
                user_id=reaction.user_id,
                reaction_type=reaction.reaction_type,
                created_at=reaction.created_at,
                user=user_dict,
            )

    def delete_reaction(self, situation_id: int, reaction_type: str, user_id: int):
        """Delete a reaction."""
        with SessionLocal() as db:
            reaction = self.repo.get_by_user_and_situation(db, user_id, situation_id)
            if reaction and reaction.reaction_type == reaction_type:
                self.repo.delete(db, reaction.id)
