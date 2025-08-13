from app.core.database import SessionLocal
from app.core.exceptions import NotFoundError
from app.repositories.topic_repository import TopicRepository
from app.schemas.topics import TopicCreate, TopicOut, TopicUpdate


class TopicService:
    def __init__(self, repo=None):
        self.repo = repo or TopicRepository()

    def list_topics(self):
        """List all topics."""
        with SessionLocal() as db:
            topics = self.repo.get_multi(db)
            return [TopicOut.from_orm(topic) for topic in topics]

    def get_topic(self, topic_id: int):
        """Get topic by ID."""
        with SessionLocal() as db:
            topic = self.repo.get(db, topic_id)
            if not topic:
                raise NotFoundError("Topic", topic_id)
            return TopicOut.from_orm(topic)

    def create_topic(self, topic_in: TopicCreate):
        """Create new topic."""
        with SessionLocal() as db:
            topic = self.repo.create(db, topic_in)
            return TopicOut.from_orm(topic)

    def update_topic(self, topic_id: int, topic_in: TopicUpdate):
        """Update topic."""
        with SessionLocal() as db:
            topic = self.repo.get(db, topic_id)
            if not topic:
                raise NotFoundError("Topic", topic_id)
            updated_topic = self.repo.update(db, topic, topic_in)
            return TopicOut.from_orm(updated_topic)

    def delete_topic(self, topic_id: int):
        """Delete topic."""
        with SessionLocal() as db:
            topic = self.repo.get(db, topic_id)
            if not topic:
                raise NotFoundError("Topic", topic_id)
            self.repo.delete(db, topic_id)
            return {"message": "Topic deleted successfully"}
