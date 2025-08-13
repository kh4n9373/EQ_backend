from app.models import Topic
from app.repositories.base import BaseRepository
from app.schemas.topics import TopicCreate, TopicUpdate


class TopicRepository(BaseRepository[Topic, TopicCreate, TopicUpdate]):
    def __init__(self):
        super().__init__(Topic)

    def get_by_name(self, db, name: str):
        return db.query(self.model).filter(self.model.name == name).first()

    def get_topic_by_id(self, db, topic_id: int):
        """Get topic by ID."""
        return self.get(db, topic_id)

    def list_topics(self, db):
        """List all topics."""
        return self.get_multi(db)
