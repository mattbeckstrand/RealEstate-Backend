from fastapi import APIRouter, UploadFile, File, HTTPException
import shutil
import os

router = APIRouter()

@router.post("/")
async def upload_file(file: UploadFile = File(...)):
    try:
        # Validate file type if needed
        allowed_types = ["text/csv", "application/json", "application/vnd.ms-excel"]
        if file.content_type not in allowed_types:
            raise HTTPException(
                status_code=400, 
                detail=f"File type {file.content_type} not supported"
            )

        # Create upload directory if it doesn't exist
        upload_dir = "uploaded_files"
        os.makedirs(upload_dir, exist_ok=True)
        
        # Save file
        file_path = f"{upload_dir}/{file.filename}"
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Return success response with file details
        return {
            "status": "success",
            "filename": file.filename,
            "file_path": file_path,
            "content_type": file.content_type,
            "size": os.path.getsize(file_path)  # File size in bytes
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to upload file: {str(e)}"
        )
