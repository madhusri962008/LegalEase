from fastapi import APIRouter, HTTPException

from backend.ai_core.gemini_generator import (
    GeminiDocumentGenerator
)

from backend.models import (
    DocumentRequest,
    DocumentResponse
)


router = APIRouter(
    prefix="/api",
    tags=["LegalEase"]
)


generator = GeminiDocumentGenerator()


@router.post(
    "/generate",
    response_model=DocumentResponse
)
def generate_document(
    request: DocumentRequest
):

    try:

        content = generator.generate_document(

            document_type=request.document_type,

            parties=request.parties,

            terms=request.terms,

            effective_date=request.effective_date,
        )

        return DocumentResponse(

            success=True,

            document_type=request.document_type,

            content=content,

            model=generator.model or "unknown",
        )

    except RuntimeError as exc:

        raise HTTPException(
            status_code=503,
            detail=str(exc)
        ) from exc

    except Exception as exc:

        raise HTTPException(
            status_code=502,
            detail=f"Document generation failed: {exc}"
        ) from exc