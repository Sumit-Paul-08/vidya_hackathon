from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from database import Base, engine
import models  # noqa: F401 (registers models with Base before create_all)
from routers import auth, ai, process

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Vidya Backend", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(ai.router)
app.include_router(process.router)


@app.get("/api/health")
def health():
    return {"status": "ok"}
