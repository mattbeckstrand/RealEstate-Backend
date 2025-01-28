from fastapi import APIRouter, UploadFile, File, HTTPException
from .analysis import analyze_data

router = APIRouter()

@router.post("/")
async def upload_file(file: UploadFile = File(...)):
    try:
        # Validate file type
        if not file.filename:
            raise HTTPException(
                status_code=400,
                detail="No filename provided"
            )
        
        filename_lower = file.filename.lower()
        valid_extensions = ('.pdf', '.xlsx', '.xls')

        if not any(filename_lower.endswith(ext) for ext in valid_extensions):
            raise HTTPException(
                status_code=400,
                detail='only pdf, xls, and xlsx files supported'
            )

        # Process file
        try:
            result = await analyze_data(file)
            return result
        except Exception as e:
            import traceback
            print(f"Analysis error at:\n{traceback.format_exc()}")  # Shows full stack trace
            raise HTTPException(
                status_code=500,
                detail=f"Error processing file: {str(e)}"
            )

    except Exception as e:
        import traceback
        print(f"Upload error at:\n{traceback.format_exc()}")
        raise HTTPException(
            status_code=500,
            detail=f"Upload failed: {str(e)}"
        )
