from fastapi import APIRouter, UploadFile, File, HTTPException
from ..services.pdf_reader import PdfTextExtractor # type: ignore
from ..services.openai_service import OpenAIService # type: ignore
from ..services.excel_reader import ExcelTextExtractor # type: ignore


router = APIRouter()

@router.post("/process")
async def analyze_data(file: UploadFile = File(...)):
    if not file.filename:
        raise HTTPException(status_code=400, detail="No filename provided")
    extractedText = []
    filename_lower = file.filename.lower()

    try:
        if filename_lower.endswith('pdf'):
            text = PdfTextExtractor.readPdf(file)
            extractedText.append(text)
        elif filename_lower.endswith(('xls', 'xlsx')):
            text = ExcelTextExtractor.readExcel(file)
            extractedText.append(text)
        else:
            raise HTTPException(
                status_code=400,
                detail="Unsuported file type"
            )
        
        aiResponse = await OpenAIService.analyze_data(extractedText)
        return {"aiResponse": aiResponse}  # Return as dictionary
   
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing file: {str(e)}"
        )