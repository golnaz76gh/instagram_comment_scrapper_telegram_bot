from sqlalchemy import Column, Integer, String, Text, TIMESTAMP
from db_setup import Base

class InstagramComment(Base):
    __tablename__ = "instagram_comments"

    id = Column(Integer, primary_key=True, index=True)
    shortcode = Column(String(255), index=True)
    comment_text = Column(Text)
    username = Column(String(255))
    timestamp = Column(TIMESTAMP)