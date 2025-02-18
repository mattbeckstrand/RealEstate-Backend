from fastapi import UploadFile
from typing import List, Dict, Any
from .data_cleaner import DataCleaner # type: ignore
import pandas as pd

class PropertyAnalysis:
    @staticmethod
    async def analyzeProperty(files: List[UploadFile], file_types: List[str]) -> Dict[str, Any]:
        """
        Analyze property files and return cleaned data.
        Currently only handling T12 statements.
        """
        cleaner = DataCleaner()
        result = {}

        for file, file_type in zip(files, file_types):
            if file_type == "t12":
                # Read the Excel file
                df = pd.read_excel(await file.read())
                
                # Clean the data using DataCleaner
                cleaned_data = cleaner.process_t12_data(df)
                
                # Convert to dictionary format for JSON response
                result["t12Data"] = {
                    "cleaned_data": cleaned_data.to_dict(orient='records'),
                    "message": "T12 data processed successfully"
                }

        return result

    
    

