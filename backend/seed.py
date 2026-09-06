"""
Run once: python seed.py
Creates the demo teacher account, matching src/services/seedData.ts's DEMO_TEACHER,
so the real backend login lines up with what the frontend already expects to show.
"""
from database import Base, engine, SessionLocal
import models

Base.metadata.create_all(bind=engine)

db = SessionLocal()

existing = db.query(models.Teacher).filter(models.Teacher.teacher_id == "T-1082").first()
if existing:
    print("Demo teacher already exists — nothing to do.")
else:
    demo_teacher = models.Teacher(
        teacher_id="T-1082",
        password="demo123",  # plain text: fine for a hackathon demo, NOT for production
        email="priya.sharma@vidya.edu",
        name="Dr. Priya Sharma",
        department="Mathematics & Computer Science",
        avatar_url="https://images.unsplash.com/photo-1573496359142-b8d87734a5a2?w=150&auto=format&fit=crop&q=80",
        preferred_language="en",
    )
    db.add(demo_teacher)
    db.commit()
    print("Demo teacher created: teacherId=T-1082, password=demo123")

db.close()
