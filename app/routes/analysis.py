from fastapi import APIRouter, UploadFile, File
from ..services.pdf_reader import PdfTextExtractor # type: ignore
from ..services.openai_service import OpenAIService # type: ignore

router = APIRouter()

@router.post("/process")
async def analyze_data(file: UploadFile = File(...)):
    text = PdfTextExtractor.readPdf(file)
    aiResponse = await OpenAIService.analyze_data(text)

    return {"aiResponse": aiResponse}  # Return as dictionary