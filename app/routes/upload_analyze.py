from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from typing import List
from ..services.analysis import PropertyAnalysis # type: ignore

router = APIRouter()

@router.post("/")
async def upload_and_analyze(
    files: List[UploadFile] = File(...),
    file_types: List[str] = Form(...)
):
    try:
        # Basic validation
        if not files:
            raise HTTPException(
                status_code=400, 
                detail={"message": "No files provided"}
            )
        
        if len(files) != len(file_types):
            raise HTTPException(
                status_code=400, 
                detail={"message": "Number of files and file types must match"}
            )

        # File type validation
        valid_types = ["om", "t12", "rr"]  # offering memo, T12, rent roll
        if not all(ft in valid_types for ft in file_types):
            raise HTTPException(
                status_code=400,
                detail={"message": f"Invalid file type. Must be one of: {valid_types}"}
            )

        # Process files and get cleaned data
        result = await PropertyAnalysis.analyzeProperty(files, file_types)
        
        # Return structured response
        return {
            "status": "success",
            "data": result,
            "rental_income": result.get("rental_income", {})
        }
    
    except Exception as e:
        import traceback
        print(f"Upload error:\n{traceback.format_exc()}")
        raise HTTPException(
            status_code=500,
            detail={"message": f"Upload failed: {str(e)}"}
        )
    

    