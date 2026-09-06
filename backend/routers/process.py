from fastapi import APIRouter, UploadFile, File, Form, HTTPException

import ai_provider
from schemas import GeneratedAccessibilityContentOut

router = APIRouter(prefix="/api", tags=["processing"])

PROCESS_SYSTEM_PROMPT = """You generate accessibility content for an inclusive-education
platform (Vidya) from a teacher-uploaded file. Analyze the attached file and respond
ONLY as strict JSON matching this shape:
{
  "imageDescription": "<detailed alt-text style description if the file contains a diagram/image, else null>",
  "mathMl": "<MathML string if the file contains a math formula worth marking up, else null>",
  "spokenMath": "<a spoken-language version of any formula, e.g. 'x equals...', else null>",
  "screenReaderStructure": "<a short outline of heading structure detected, e.g. 'H1: ... H2: ...', else null>",
  "transcript": "<transcript or extracted plain text of the content, else null>",
  "simplifiedText": "<a simplified, plain-language explanation of the core content, 2-4 sentences>",
  "confidence": <float 0.0-1.0, your confidence in this analysis>
}
Only fill fields that genuinely apply to this file type; use null for the rest.
"""

# Map our ResourceType to a mime type Gemini understands for file input
MIME_BY_RESOURCE_TYPE = {
    "pdf": "application/pdf",
    "image": "image/jpeg",  # overridden by actual upload content_type when available
    "doc": "application/pdf",  # best effort — most teacher docs get exported/uploaded as pdf/image
    "presentation": "application/pdf",
    "video": None,  # not sent as file; handled via text-only fallback below
    "audio": None,
}


@router.post("/process-resource", response_model=GeneratedAccessibilityContentOut)
async def process_resource(
    file: UploadFile = File(...),
    resourceType: str = Form(...),
    title: str = Form(""),
):
    try:
        file_bytes = await file.read()
        mime_type = file.content_type or MIME_BY_RESOURCE_TYPE.get(resourceType) or "application/octet-stream"

        prompt = f'Resource title: "{title}". Resource type: {resourceType}.'

        if resourceType in ("video", "audio") or not file_bytes:
            # We don't have real video/audio understanding wired up yet on the free tier —
            # fall back to a text-only prompt using just the title/type so the pipeline
            # still returns something honest rather than fabricating a transcript.
            prompt += (
                " No file content could be analyzed directly for this media type in this "
                "demo build — base your response only on the title and type given."
            )
            result = ai_provider.generate_json(prompt, system_instruction=PROCESS_SYSTEM_PROMPT)
        else:
            result = ai_provider.generate_json_from_file(
                file_bytes=file_bytes,
                mime_type=mime_type,
                prompt=prompt,
                system_instruction=PROCESS_SYSTEM_PROMPT,
            )

        return GeneratedAccessibilityContentOut(
            imageDescription=result.get("imageDescription"),
            mathMl=result.get("mathMl"),
            spokenMath=result.get("spokenMath"),
            screenReaderStructure=result.get("screenReaderStructure"),
            transcript=result.get("transcript"),
            simplifiedText=result.get("simplifiedText"),
            confidence=float(result.get("confidence", 0.85)),
            teacherApproved=False,
        )
    except ai_provider.AIProviderError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Processing failed: {e}")
