import uuid
from sqlalchemy import Column, String, Boolean
from database import Base


def gen_id():
    return uuid.uuid4().hex[:12]


class Teacher(Base):
    """
    Minimal Teacher table for real auth. Matches the shape the frontend's
    User type expects (see src/types/index.ts) for role='teacher'.
    """
    __tablename__ = "teachers"

    id = Column(String, primary_key=True, default=gen_id)
    teacher_id = Column(String, unique=True, index=True, nullable=False)  # e.g. "T-1082"
    password = Column(String, nullable=False)  # plain text: OK for a hackathon demo only
    email = Column(String, nullable=False)
    name = Column(String, nullable=False)
    department = Column(String, nullable=True)
    avatar_url = Column(String, nullable=True)
    preferred_language = Column(String, default="en")


class Session(Base):
    """Very small token store — maps an opaque token to a teacher_id."""
    __tablename__ = "sessions"

    token = Column(String, primary_key=True, default=lambda: uuid.uuid4().hex)
    teacher_id = Column(String, nullable=False)
