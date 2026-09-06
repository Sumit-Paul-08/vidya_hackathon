import uuid
from fastapi import APIRouter, HTTPException

import ai_provider
from schemas import (
    AIChatInput,
    AIChatOutput,
    SimplifyRequest,
    SimplifyResponse,
    TranslateRequest,
    TranslateResponse,
    QuizAnalysisRequest,
    QuizAnalysisResponse,
)

router = APIRouter(prefix="/api/ai", tags=["ai"])

TUTOR_SYSTEM_PROMPT = """You are Vidya, an AI tutor inside an inclusive-education app for
students with visual, hearing, cognitive, or motor accessibility needs. Always:
- Explain clearly and step by step, in accessible, plain language.
- If the question is math/science, show the formula and a worked example.
- Keep answers focused — no filler, no "As an AI" disclaimers.
Respond ONLY as strict JSON matching this shape:
{
  "content": "<markdown-formatted answer>",
  "suggestedFollowups": ["<follow-up question 1>", "<follow-up question 2>"],
  "uncertaintyWarning": "<string or null, only if the question was too vague to answer well>"
}
"""


@router.post("/chat", response_model=AIChatOutput)
def chat(payload: AIChatInput):
    try:
        context_bits = []
        if payload.courseContext:
            context_bits.append(f"Course: {payload.courseContext}")
        if payload.lessonContext:
            context_bits.append(f"Lesson: {payload.lessonContext}")
        if payload.learningLevel:
            context_bits.append(f"Student's learning level: {payload.learningLevel}")
        if payload.language == "hi":
            context_bits.append("Respond in Hindi.")
        context_str = ("\n".join(context_bits) + "\n\n") if context_bits else ""

        prompt = f"{context_str}Student's question: {payload.message}"
        result = ai_provider.generate_json(prompt, system_instruction=TUTOR_SYSTEM_PROMPT)

        return AIChatOutput(
            id=f"msg_{uuid.uuid4().hex[:10]}",
            role="assistant",
            content=result.get("content", "Sorry, I couldn't generate a response."),
            suggestedFollowups=result.get("suggestedFollowups", []) or [],
            uncertaintyWarning=result.get("uncertaintyWarning") or None,
        )
    except ai_provider.AIProviderError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI generation failed: {e}")


@router.post("/simplify", response_model=SimplifyResponse)
def simplify(payload: SimplifyRequest):
    try:
        prompt = (
            f'Rewrite the following text so it is understandable at a "{payload.level}" '
            f"level. Keep it accurate but much simpler. Return ONLY the rewritten text, "
            f"no preamble.\n\nText:\n{payload.text}"
        )
        text = ai_provider.generate_text(prompt)
        return SimplifyResponse(simplifiedText=text)
    except ai_provider.AIProviderError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI generation failed: {e}")


@router.post("/translate", response_model=TranslateResponse)
def translate(payload: TranslateRequest):
    try:
        prompt = (
            f"Translate the following text to Hindi. Return ONLY the Hindi translation, "
            f"no preamble, no English.\n\nText:\n{payload.text}"
        )
        text = ai_provider.generate_text(prompt)
        return TranslateResponse(translatedText=text)
    except ai_provider.AIProviderError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI generation failed: {e}")


@router.post("/analyze-quiz", response_model=QuizAnalysisResponse)
def analyze_quiz(payload: QuizAnalysisRequest):
    try:
        prompt = (
            f"A student scored {payload.scorePercent}% on a quiz. "
            f"Weak topics: {', '.join(payload.weakTopics) if payload.weakTopics else 'none identified'}. "
            f'Return JSON: {{"summary": "<1-2 sentence performance summary>", '
            f'"recommendation": "<1-2 sentence specific next step>"}}'
        )
        result = ai_provider.generate_json(prompt)
        return QuizAnalysisResponse(
            summary=result.get("summary", ""),
            recommendation=result.get("recommendation", ""),
        )
    except ai_provider.AIProviderError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI generation failed: {e}")
