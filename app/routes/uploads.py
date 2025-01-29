from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from typing import List
from .analysis import analyze_data

router = APIRouter()

@router.post("/")
async def upload_files(
    files: List[UploadFile] = File(...),
    file_types: List[str] = Form(...)
):
    try:
        if not files or len(files) == 0:
            raise HTTPException(
                status_code=400,
                detail="No files provided"
            )
        
        if len(files) != len(file_types):
            raise HTTPException(
                status_code=400,
                detail="Number of files and file types must match"
            )
        
        results = []
        for file, file_type in zip(files, file_types):
            if not file.filename:
                raise HTTPException(
                    status_code=400,
                    detail="No filename provided"
                )
            
            # Validate file extension based on type
            filename_lower = file.filename.lower()
            if file_type == 'om' and not filename_lower.endswith('.pdf'):
                raise HTTPException(
                    status_code=400,
                    detail=f"Offering Memorandum '{file.filename}' must be a PDF file"
                )
            elif file_type in ['rent_roll', 'financials'] and not any(
                filename_lower.endswith(ext) for ext in ['.xls', '.xlsx']
            ):
                raise HTTPException(
                    status_code=400,
                    detail=f"{file_type.title()} '{file.filename}' must be an Excel file"
                )

            try:
                result = await analyze_data(file=file, file_type=file_type)
                results.append({
                    "filename": file.filename,
                    "file_type": file_type,
                    "analysis": result
                })
            except Exception as e:
                import traceback
                print(f"Analysis error for file {file.filename}:\n{traceback.format_exc()}")
                raise HTTPException(
                    status_code=500,
                    detail=f"Error processing file {file.filename}: {str(e)}"
                )

        return results

    except Exception as e:
        import traceback
        print(f"Upload error:\n{traceback.format_exc()}")
        raise HTTPException(
            status_code=500,
            detail=f"Upload failed: {str(e)}"
        )
