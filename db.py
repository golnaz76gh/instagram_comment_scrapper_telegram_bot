import logging
from sqlalchemy.exc import OperationalError
from logging_config import setup_logging
from db_setup import Base, engine, SessionLocal
from models import InstagramComment
from datetime import datetime

# Set up logging
setup_logging()

def create_tables():
    """Create database tables if they do not exist."""
    try:
        Base.metadata.create_all(bind=engine)
        logging.info("Tables created successfully.")
    except OperationalError as e:
        logging.error(f"Error creating tables: {e}")

def save_comments_to_db(shortcode, comments):
    """Save extracted comments to the database."""
    session = SessionLocal()
    try:
        for edge in comments["data"]["shortcode_media"]["edge_media_to_comment"]["edges"]:
            comment = edge["node"]["text"]
            username = edge["node"]["owner"]["username"]
            timestamp = edge["node"]["created_at"]

            # Convert timestamp from integer to datetime
            timestamp = datetime.fromtimestamp(timestamp)

            db_comment = InstagramComment(
                shortcode=shortcode,
                comment_text=comment,
                username=username,
                timestamp=timestamp
            )
            session.add(db_comment)
        session.commit()  # Make sure to commit the session after adding all comments
        logging.info(f'Saved comments to database for shortcode: {shortcode}')
    except Exception as e:
        logging.error(f"Error saving comments to the database: {e}")
        session.rollback()  # Rollback in case of error
    finally:
        session.close()  # Ensure the session is closed after use