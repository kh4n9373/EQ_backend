from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.models import Situation, Topic


def seed():
    db: Session = SessionLocal()
    topics = [
        Topic(name="Tình yêu"),
        Topic(name="Công sở"),
        Topic(name="Gia đình"),
        Topic(name="Bạn bè"),
    ]
    for topic in topics:
        if not db.query(Topic).filter_by(name=topic.name).first():
            db.add(topic)
    db.commit()
    love = db.query(Topic).filter_by(name="Tình yêu").first()
    work = db.query(Topic).filter_by(name="Công sở").first()
    family = db.query(Topic).filter_by(name="Gia đình").first()
    friends = db.query(Topic).filter_by(name="Bạn bè").first()
    situations = [
        Situation(
            topic_id=love.id,
            context="Người yêu bạn tỏ ra lạnh nhạt, bạn nghi ngờ có người thứ ba.",
            question="Bạn sẽ làm gì và nói gì với người yêu trong tình huống này?",
        ),
        Situation(
            topic_id=work.id,
            context="Đồng nghiệp liên tục trễ deadline khiến nhóm bị ảnh hưởng.",
            question="Bạn sẽ xử lý thế nào với đồng nghiệp này?",
        ),
        Situation(
            topic_id=family.id,
            context="Cha mẹ thường xuyên so sánh bạn với người khác.",
            question="Bạn sẽ phản ứng ra sao khi bị so sánh?",
        ),
        Situation(
            topic_id=friends.id,
            context="Bạn phát hiện bạn thân nói xấu mình sau lưng.",
            question="Bạn sẽ đối diện và giải quyết như thế nào?",
        ),
    ]
    for s in situations:
        exists = (
            db.query(Situation)
            .filter_by(context=s.context, question=s.question)
            .first()
        )
        if not exists:
            db.add(s)
    db.commit()
    db.close()
    print("Đã seed dữ liệu mẫu!")


if __name__ == "__main__":
    seed()
