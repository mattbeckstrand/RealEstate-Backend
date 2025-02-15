from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from typing import List # type: ignore
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
            raise HTTPException(status_code=400, detail="No files provided")
        
        if len(files) != len(file_types):
            raise HTTPException(
                status_code=400, 
                detail="Number of files and file types must match"
            )

        # File type validation
        valid_types = {"om", "t12", "rr"}  # offering memo, T12, rent roll
        if not all(ft in valid_types for ft in file_types):
            raise HTTPException(
                status_code=400,
                detail=f"Invalid file type. Must be one of: {valid_types}"
            )
        t12Text = PropertyAnalysis.analyzeProperty(files[0], file_types[0])
        return t12Text
    
    except Exception as e:
        import traceback
        print(f"Upload error:\n{traceback.format_exc()}")
        raise HTTPException(
            status_code=500,
            detail={f"Upload failed: {str(e)}"}
        )
    

    