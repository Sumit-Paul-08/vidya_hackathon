from typing import Optional, List, Dict
from pydantic import BaseModel


# ---------- Auth ----------

class TeacherLoginRequest(BaseModel):
    teacherId: str
    password: str


class UserOut(BaseModel):
    id: str
    email: str
    role: str
    name: str
    avatarUrl: Optional[str] = ""
    preferredLanguage: str = "en"
    teacherId: Optional[str] = None
    department: Optional[str] = None


class TeacherLoginResponse(BaseModel):
    user: UserOut
    token: str


# ---------- AI Chat (matches src/services/aiService.ts) ----------

class AIChatInput(BaseModel):
    message: str
    courseContext: Optional[str] = None
    lessonContext: Optional[str] = None
    learningLevel: Optional[str] = None
    language: Optional[str] = "en"


class SpecificTermCallout(BaseModel):
    term: str
    definition: str


class AIChatOutput(BaseModel):
    id: str
    role: str = "assistant"
    content: str
    mathMl: Optional[str] = None
    tableData: Optional[Dict] = None
    suggestedFollowups: List[str] = []
    uncertaintyWarning: Optional[str] = None
    specificTermCallout: Optional[SpecificTermCallout] = None


class SimplifyRequest(BaseModel):
    text: str
    level: str


class SimplifyResponse(BaseModel):
    simplifiedText: str


class TranslateRequest(BaseModel):
    text: str


class TranslateResponse(BaseModel):
    translatedText: str


class QuizAnalysisRequest(BaseModel):
    scorePercent: float
    weakTopics: List[str] = []


class QuizAnalysisResponse(BaseModel):
    summary: str
    recommendation: str


# ---------- Content Processing (matches GeneratedAccessibilityContent) ----------

class GeneratedAccessibilityContentOut(BaseModel):
    imageDescription: Optional[str] = None
    mathMl: Optional[str] = None
    spokenMath: Optional[str] = None
    screenReaderStructure: Optional[str] = None
    transcript: Optional[str] = None
    simplifiedText: Optional[str] = None
    confidence: float = 0.9
    teacherApproved: bool = False
