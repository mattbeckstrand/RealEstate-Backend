import PyPDF2
from fastapi import UploadFile
import asyncio
from typing import List
from io import BytesIO

class PdfTextExtractor:
    @staticmethod
    async def readPdf(file: UploadFile) -> str:
        """Read and extract text from PDF files."""
        try:
            # Read the file content
            contents = await file.read()
            
            def extract_text_from_pdf(pdf_bytes: bytes) -> str:
                # Create PDF reader from bytes
                pdf_reader = PyPDF2.PdfReader(BytesIO(pdf_bytes))
                text_parts: List[str] = []
                
                # Extract text from each page
                for page_num in range(len(pdf_reader.pages)):
                    page = pdf_reader.pages[page_num]
                    text = page.extract_text()
                    if text:  # Only add non-empty pages
                        text_parts.append(text)
                
                return "\n\n=== Page Break ===\n\n".join(text_parts)
            
            # Run PDF processing in a thread pool
            text = await asyncio.to_thread(extract_text_from_pdf, contents)
            return text
            
        except Exception as e:
            print(f"Error reading PDF file: {str(e)}")
            raise Exception(f"Failed to read PDF file: {str(e)}")
        finally:
            # Reset file pointer
            await file.seek(0)
