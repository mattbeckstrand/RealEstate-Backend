from fastapi import APIRouter, UploadFile, File
import pandas as pd  # for data processing

router = APIRouter()

@router.post("/analyze-file")
async def analyze_data(file: UploadFile = File(...)):
    # Read file content (example with CSV)
    df = pd.read_csv(file.file)
    
    # Perform analysis
    analysis_result = {
        "total_rows": len(df),
        "columns": df.columns.tolist(),
        "summary": df.describe().to_dict()
    }
    
    return analysis_result