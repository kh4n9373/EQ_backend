import pytest
from sqlalchemy.orm import Session

from app.models import Comment, Reaction, Situation, Topic, User
from app.services.situation_service import SituationService


def _seed_data(db: Session):
    u1 = User(email="u1@ex.com", name="U1")
    u2 = User(email="u2@ex.com", name="U2")
    db.add_all([u1, u2])
    db.commit()
    db.refresh(u1)
    db.refresh(u2)

    t1 = Topic(name="FeedTopic1")
    db.add(t1)
    db.commit()
    db.refresh(t1)

    s1 = Situation(topic_id=t1.id, user_id=u1.id, context="c1", question="q1?")
    s2 = Situation(topic_id=t1.id, user_id=u2.id, context="c2", question="q2?")
    db.add_all([s1, s2])
    db.commit()
    db.refresh(s1)
    db.refresh(s2)

    c11 = Comment(situation_id=s1.id, user_id=u2.id, content="hi")
    c12 = Comment(situation_id=s1.id, user_id=u1.id, content="hi2")
    db.add_all([c11, c12])

    r11 = Reaction(situation_id=s1.id, user_id=u2.id, reaction_type="upvote")
    r12 = Reaction(situation_id=s1.id, user_id=u1.id, reaction_type="downvote")
    db.add_all([r11, r12])

    db.commit()
    return u1, u2, t1, s1, s2


def test_get_situations_feed_paginated_and_by_user(db_session: Session):
    svc = SituationService()
    u1, u2, t1, s1, s2 = _seed_data(db_session)

    feed = svc.get_situations_feed_paginated(page=1, limit=10)
    assert "items" in feed and isinstance(feed["items"], list)
    assert any(item["id"] == s1.id for item in feed["items"])  # has stats

    feed_u1 = svc.get_situations_by_user_with_feed(user_id=u1.id, current_user_id=u2.id)
    assert isinstance(feed_u1, list) and any(item["id"] == s1.id for item in feed_u1)


def test_get_contributed_situations_format(db_session: Session):
    svc = SituationService()
    _seed_data(db_session)
    out = svc.get_contributed_situations()
    assert isinstance(out, list)
    # each item has stats and user keys
    if out:
        item = out[0]
        assert "stats" in item and "user" in item
