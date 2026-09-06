import uuid
from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session as DBSession

from database import get_db
import models
from schemas import TeacherLoginRequest, TeacherLoginResponse, UserOut

router = APIRouter(prefix="/api", tags=["auth"])


def _teacher_to_user_out(t: models.Teacher) -> UserOut:
    return UserOut(
        id=t.id,
        email=t.email,
        role="teacher",
        name=t.name,
        avatarUrl=t.avatar_url or "",
        preferredLanguage=t.preferred_language or "en",
        teacherId=t.teacher_id,
        department=t.department,
    )


@router.post("/auth/teacher-login", response_model=TeacherLoginResponse)
def teacher_login(payload: TeacherLoginRequest, db: DBSession = Depends(get_db)):
    normalized_id = payload.teacherId.strip().upper()
    teacher = (
        db.query(models.Teacher)
        .filter(models.Teacher.teacher_id.ilike(normalized_id))
        .first()
    )

    if not teacher or teacher.password != payload.password:
        raise HTTPException(status_code=404, detail="Login failed")

    token = uuid.uuid4().hex
    db.add(models.Session(token=token, teacher_id=teacher.teacher_id))
    db.commit()

    return TeacherLoginResponse(user=_teacher_to_user_out(teacher), token=token)


@router.get("/me")
def get_me(authorization: str = Header(default=""), db: DBSession = Depends(get_db)):
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Not authenticated")

    token = authorization.removeprefix("Bearer ").strip()
    session = db.query(models.Session).filter(models.Session.token == token).first()
    if not session:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    teacher = (
        db.query(models.Teacher)
        .filter(models.Teacher.teacher_id == session.teacher_id)
        .first()
    )
    if not teacher:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    return {"user": _teacher_to_user_out(teacher)}
