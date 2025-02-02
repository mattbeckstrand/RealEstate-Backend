from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from typing import Dict, Any
from ..services.openai_service import OpenAIService # type: ignore
from ..services.pdf_reader import PdfTextExtractor # type: ignore
from ..services.excel_reader import ExcelTextExtractor # type: ignore

router = APIRouter()

@router.post("/")
async def analyze_data(file: UploadFile = File(...), file_type: str = "") -> Dict[str, Any]:
    try:
        if not file.filename:
            raise HTTPException(status_code=400, detail="No filename provided")

        filename_lower = file.filename.lower()
        
        # Extract text based on file type
        try:
            if file_type == 'om' and filename_lower.endswith('.pdf'):
                text = await PdfTextExtractor.readPdf(file)
            elif file_type in ['rent_roll', 'financials'] and any(
                filename_lower.endswith(ext) for ext in ['.xls', '.xlsx']
            ):
                df = await ExcelTextExtractor.readExcel(file)

                # if file_type == 'rent_roll':
                #     text = ExcelTextExtractor._process_rent_roll(df)
                # elif file_type == 'financials':
                #     text = ExcelTextExtractor._process_financials(df)
                # else:
                #     text = ExcelTextExtractor._process_general_data(df)
            else:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid file type or extension for {file.filename}"
                )

            # Process the extracted text with OpenAI
            # result = await OpenAIService.analyze_data(text, file_type)
            return df
            
        except Exception as e:
            print(f"Error processing file {file.filename}: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Error processing file {file.filename}: {str(e)}"
            )
            
    except Exception as e:
        print(f"Analysis error:\n{str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error processing file {file.filename}: {str(e)}"
        )