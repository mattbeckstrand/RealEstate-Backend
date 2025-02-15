from .excel_reader import ExcelTextExtractor # type: ignore
from fastapi import UploadFile
from typing import List

class PropertyAnalysis:
    @staticmethod
    async def analyzeProperty(files: List[UploadFile], file_types: List[str]) -> str:
        try:
            for file in files:
           
                if file_types[files.index(file)] == "t12":
                    t12Text = await ExcelTextExtractor.readExcel(file)
            
            return t12Text
        
        except Exception as e:
            print(f"Error in Analysis extracting text: {str(e)}")
            raise Exception(f"Error in Analysis extracting text: {str(e)}")

    
    

