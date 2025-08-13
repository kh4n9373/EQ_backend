import time

from app.core.database import SessionLocal
from app.core.exceptions import NotFoundError
from app.core.metrics import DB_QUERY_DURATION, SITUATIONS_CREATED
from app.models import Comment, Reaction, User
from app.repositories.situation_repository import SituationRepository
from app.repositories.topic_repository import TopicRepository
from app.schemas.situations import (
    SituationBase,
    SituationContributeOut,
    SituationCreate,
    SituationOut,
    SituationUpdate,
)


class SituationService:
    def __init__(self, repo=None):
        self.repo = repo or SituationRepository()

    def get_situations_by_topic(self, topic_id: int):
        """Get situations by topic ID."""
        with SessionLocal() as db:
            situations = self.repo.get_by_topic(db, topic_id)
            return [SituationOut.from_orm(situation) for situation in situations]

    def get_contributed_situations(self):
        """Get all contributed situations with user info."""
        start_time = time.time()
        with SessionLocal() as db:
            situations = self.repo.get_contributed_situations_with_user_info(db)
            result = []
            for situation in situations:
                user_dict = None
                if hasattr(situation, "user") and situation.user:
                    user_dict = {
                        "id": situation.user.id,
                        "name": situation.user.name,
                        "picture": situation.user.picture,
                    }

                comments_count = (
                    db.query(Comment)
                    .filter(Comment.situation_id == situation.id)
                    .count()
                )
                reactions_count = (
                    db.query(Reaction)
                    .filter(Reaction.situation_id == situation.id)
                    .count()
                )
                upvotes_count = (
                    db.query(Reaction)
                    .filter(
                        Reaction.situation_id == situation.id,
                        Reaction.reaction_type == "upvote",
                    )
                    .count()
                )
                downvotes_count = (
                    db.query(Reaction)
                    .filter(
                        Reaction.situation_id == situation.id,
                        Reaction.reaction_type == "downvote",
                    )
                    .count()
                )

                result.append(
                    {
                        "id": situation.id,
                        "topic_id": situation.topic_id,
                        "user_id": situation.user_id,
                        "user": user_dict,
                        "image_url": getattr(situation, "image_url", None),
                        "context": situation.context,
                        "question": situation.question,
                        "created_at": (
                            situation.created_at.strftime("%Y-%m-%d %H:%M:%S")
                            if situation.created_at
                            else ""
                        ),
                        "stats": {
                            "comments_count": comments_count,
                            "reactions_count": reactions_count,
                            "upvotes_count": upvotes_count,
                            "downvotes_count": downvotes_count,
                        },
                    }
                )
            duration = time.time() - start_time
            DB_QUERY_DURATION.labels(
                operation="feed_query", table="situations"
            ).observe(duration)

            return result

    def get_situations_feed(self):
        """Get situations feed (deprecated, use get_situations_feed_paginated)."""
        return self.get_contributed_situations()

    def get_situations_feed_paginated(
        self,
        page: int = 1,
        limit: int = 10,
        sort_by: str = "created_at",
        sort_order: str = "desc",
        current_user_id: int = None,
    ):
        """Get situations feed with pagination and sorting, including user's reaction."""
        with SessionLocal() as db:
            if page < 1:
                page = 1
            if limit < 1 or limit > 100:
                limit = 10

            from sqlalchemy import case, func

            comments_subquery = (
                db.query(
                    Comment.situation_id, func.count(Comment.id).label("comments_count")
                )
                .group_by(Comment.situation_id)
                .subquery()
            )

            reactions_subquery = (
                db.query(
                    Reaction.situation_id,
                    func.count(Reaction.id).label("reactions_count"),
                    func.sum(
                        case((Reaction.reaction_type == "upvote", 1), else_=0)
                    ).label("upvotes_count"),
                    func.sum(
                        case((Reaction.reaction_type == "downvote", 1), else_=0)
                    ).label("downvotes_count"),
                )
                .group_by(Reaction.situation_id)
                .subquery()
            )

            if current_user_id is not None:
                user_reaction_subquery = (
                    db.query(
                        Reaction.situation_id,
                        Reaction.reaction_type.label("user_reaction"),
                    )
                    .filter(Reaction.user_id == current_user_id)
                    .subquery()
                )

                query = (
                    db.query(
                        self.repo.model,
                        User,
                        func.coalesce(comments_subquery.c.comments_count, 0).label(
                            "comments_count"
                        ),
                        func.coalesce(reactions_subquery.c.reactions_count, 0).label(
                            "reactions_count"
                        ),
                        func.coalesce(reactions_subquery.c.upvotes_count, 0).label(
                            "upvotes_count"
                        ),
                        func.coalesce(reactions_subquery.c.downvotes_count, 0).label(
                            "downvotes_count"
                        ),
                        user_reaction_subquery.c.user_reaction,
                    )
                    .outerjoin(User, self.repo.model.user_id == User.id)
                    .outerjoin(
                        comments_subquery,
                        self.repo.model.id == comments_subquery.c.situation_id,
                    )
                    .outerjoin(
                        reactions_subquery,
                        self.repo.model.id == reactions_subquery.c.situation_id,
                    )
                    .outerjoin(
                        user_reaction_subquery,
                        self.repo.model.id == user_reaction_subquery.c.situation_id,
                    )
                )
            else:
                query = (
                    db.query(
                        self.repo.model,
                        User,
                        func.coalesce(comments_subquery.c.comments_count, 0).label(
                            "comments_count"
                        ),
                        func.coalesce(reactions_subquery.c.reactions_count, 0).label(
                            "reactions_count"
                        ),
                        func.coalesce(reactions_subquery.c.upvotes_count, 0).label(
                            "upvotes_count"
                        ),
                        func.coalesce(reactions_subquery.c.downvotes_count, 0).label(
                            "downvotes_count"
                        ),
                    )
                    .outerjoin(User, self.repo.model.user_id == User.id)
                    .outerjoin(
                        comments_subquery,
                        self.repo.model.id == comments_subquery.c.situation_id,
                    )
                    .outerjoin(
                        reactions_subquery,
                        self.repo.model.id == reactions_subquery.c.situation_id,
                    )
                )

            query = query.filter(self.repo.model.topic_id.isnot(None))

            if sort_by == "created_at":
                if sort_order == "desc":
                    query = query.order_by(self.repo.model.created_at.desc())
                else:
                    query = query.order_by(self.repo.model.created_at.asc())

            total_count = (
                db.query(self.repo.model)
                .filter(self.repo.model.topic_id.isnot(None))
                .count()
            )

            offset = (page - 1) * limit
            results = query.offset(offset).limit(limit).all()

            result = []
            for row in results:
                if current_user_id is not None:
                    (
                        situation,
                        user,
                        comments_count,
                        reactions_count,
                        upvotes_count,
                        downvotes_count,
                        user_reaction,
                    ) = row
                else:
                    (
                        situation,
                        user,
                        comments_count,
                        reactions_count,
                        upvotes_count,
                        downvotes_count,
                    ) = row
                    user_reaction = None

                user_dict = None
                if user:
                    user_dict = {
                        "id": user.id,
                        "name": user.name,
                        "picture": user.picture,
                    }

                result.append(
                    {
                        "id": situation.id,
                        "topic_id": situation.topic_id,
                        "user_id": situation.user_id,
                        "user": user_dict,
                        "image_url": getattr(situation, "image_url", None),
                        "context": situation.context,
                        "question": situation.question,
                        "created_at": (
                            situation.created_at.strftime("%Y-%m-%d %H:%M:%S")
                            if situation.created_at
                            else ""
                        ),
                        "stats": {
                            "comments_count": int(comments_count),
                            "reactions_count": int(reactions_count),
                            "upvotes_count": int(upvotes_count),
                            "downvotes_count": int(downvotes_count),
                        },
                        "user_reaction": user_reaction,
                    }
                )

            return {
                "items": result,
                "pagination": {
                    "page": page,
                    "limit": limit,
                    "total": total_count,
                    "pages": (total_count + limit - 1) // limit,
                    "has_next": page * limit < total_count,
                    "has_prev": page > 1,
                },
            }

    def get_situation(self, situation_id: int):
        """Get situation by ID."""
        with SessionLocal() as db:
            situation = self.repo.get(db, situation_id)
            if not situation:
                raise NotFoundError("Situation", situation_id)
            return SituationOut.from_orm(situation)

    def create_situation(self, situation_in: SituationBase, user_id):
        """Create new situation."""
        situation_data = situation_in.dict()
        if situation_data.get("topic_id"):
            topic_repo = TopicRepository()
            with SessionLocal() as db:
                topic = topic_repo.get(db, situation_data["topic_id"])
                if not topic:
                    situation_data["topic_id"] = None

        situation = SituationCreate(**situation_data, user_id=user_id)
        with SessionLocal() as db:
            situation = self.repo.create(db, situation)
            return SituationOut.from_orm(situation)

    def contribute_situation(self, situation_data: dict, user_id: int):
        """Create a contributed situation."""
        SITUATIONS_CREATED.inc()
        with SessionLocal() as db:
            situation = self.repo.create_contributed_situation(
                db, situation_data, user_id
            )
            return SituationContributeOut.from_orm(situation)

    def update_situation(self, situation_id: int, situation_in: SituationUpdate):
        """Update situation."""
        with SessionLocal() as db:
            situation = self.repo.get(db, situation_id)
            if not situation:
                raise NotFoundError("Situation", situation_id)
            updated_situation = self.repo.update(db, situation, situation_in)
            return SituationOut.from_orm(updated_situation)

    def delete_situation(self, situation_id: int):
        """Delete situation."""
        with SessionLocal() as db:
            situation = self.repo.get(db, situation_id)
            if not situation:
                raise NotFoundError("Situation", situation_id)
            self.repo.delete(db, situation_id)
            return {"message": "Situation deleted successfully"}

    def get_situations_by_user(self, user_id: int):
        """Get situations by user ID."""
        with SessionLocal() as db:
            situations = self.repo.get_by_user(db, user_id)
            return [SituationOut.from_orm(situation) for situation in situations]

    def get_situations_by_user_with_feed(
        self, user_id: int, current_user_id: int = None
    ):
        """Get situations by user ID with user info and stats for feed display."""
        with SessionLocal() as db:
            from sqlalchemy import case, func

            comments_subquery = (
                db.query(
                    Comment.situation_id, func.count(Comment.id).label("comments_count")
                )
                .group_by(Comment.situation_id)
                .subquery()
            )

            reactions_subquery = (
                db.query(
                    Reaction.situation_id,
                    func.count(Reaction.id).label("reactions_count"),
                    func.sum(
                        case((Reaction.reaction_type == "upvote", 1), else_=0)
                    ).label("upvotes_count"),
                    func.sum(
                        case((Reaction.reaction_type == "downvote", 1), else_=0)
                    ).label("downvotes_count"),
                )
                .group_by(Reaction.situation_id)
                .subquery()
            )

            if current_user_id is not None:
                user_reaction_subquery = (
                    db.query(
                        Reaction.situation_id,
                        Reaction.reaction_type.label("user_reaction"),
                    )
                    .filter(Reaction.user_id == current_user_id)
                    .subquery()
                )

                query = (
                    db.query(
                        self.repo.model,
                        User,
                        func.coalesce(comments_subquery.c.comments_count, 0).label(
                            "comments_count"
                        ),
                        func.coalesce(reactions_subquery.c.reactions_count, 0).label(
                            "reactions_count"
                        ),
                        func.coalesce(reactions_subquery.c.upvotes_count, 0).label(
                            "upvotes_count"
                        ),
                        func.coalesce(reactions_subquery.c.downvotes_count, 0).label(
                            "downvotes_count"
                        ),
                        user_reaction_subquery.c.user_reaction,
                    )
                    .outerjoin(User, self.repo.model.user_id == User.id)
                    .outerjoin(
                        comments_subquery,
                        self.repo.model.id == comments_subquery.c.situation_id,
                    )
                    .outerjoin(
                        reactions_subquery,
                        self.repo.model.id == reactions_subquery.c.situation_id,
                    )
                    .outerjoin(
                        user_reaction_subquery,
                        self.repo.model.id == user_reaction_subquery.c.situation_id,
                    )
                )
            else:
                query = (
                    db.query(
                        self.repo.model,
                        User,
                        func.coalesce(comments_subquery.c.comments_count, 0).label(
                            "comments_count"
                        ),
                        func.coalesce(reactions_subquery.c.reactions_count, 0).label(
                            "reactions_count"
                        ),
                        func.coalesce(reactions_subquery.c.upvotes_count, 0).label(
                            "upvotes_count"
                        ),
                        func.coalesce(reactions_subquery.c.downvotes_count, 0).label(
                            "downvotes_count"
                        ),
                    )
                    .outerjoin(User, self.repo.model.user_id == User.id)
                    .outerjoin(
                        comments_subquery,
                        self.repo.model.id == comments_subquery.c.situation_id,
                    )
                    .outerjoin(
                        reactions_subquery,
                        self.repo.model.id == reactions_subquery.c.situation_id,
                    )
                )

            query = query.filter(self.repo.model.user_id == user_id)
            query = query.order_by(self.repo.model.created_at.desc())

            results = query.all()

            result = []
            for row in results:
                if current_user_id is not None:
                    (
                        situation,
                        user,
                        comments_count,
                        reactions_count,
                        upvotes_count,
                        downvotes_count,
                        user_reaction,
                    ) = row
                else:
                    (
                        situation,
                        user,
                        comments_count,
                        reactions_count,
                        upvotes_count,
                        downvotes_count,
                    ) = row
                    user_reaction = None

                user_dict = None
                if user:
                    user_dict = {
                        "id": user.id,
                        "name": user.name,
                        "picture": user.picture,
                    }

                result.append(
                    {
                        "id": situation.id,
                        "topic_id": situation.topic_id,
                        "user_id": situation.user_id,
                        "user": user_dict,
                        "image_url": getattr(situation, "image_url", None),
                        "context": situation.context,
                        "question": situation.question,
                        "created_at": (
                            situation.created_at.strftime("%Y-%m-%d %H:%M:%S")
                            if situation.created_at
                            else ""
                        ),
                        "stats": {
                            "comments_count": int(comments_count),
                            "reactions_count": int(reactions_count),
                            "upvotes_count": int(upvotes_count),
                            "downvotes_count": int(downvotes_count),
                        },
                        "user_reaction": user_reaction,
                    }
                )
            return result
