from pypdf import PdfReader
import io
import re

class PdfTextExtractor: 
    @staticmethod
    def readPdf(pdfFile):
        try:
            # Read file content
            content = pdfFile.file.read()
            
            # Create PDF reader
            pdf = PdfReader(io.BytesIO(content))
            
            important_text = []
            keywords = [
                'price', 'sqft', 'bedroom', 'bath', 'address',
                'property', 'type', 'year', 'built', 'lot',
                'garage', 'tax', 'zoning', 'value'
            ]
            
            for page in pdf.pages:
                text = page.extract_text()
                # Split into lines and filter important ones
                lines = text.split('\n')
                filtered_lines = [
                    line.strip() for line in lines
                    if any(keyword in line.lower() for keyword in keywords)
                ]
                if filtered_lines:
                    important_text.extend(filtered_lines)
            
            return important_text
            
        except Exception as e:
            print(f"PDF reading error: {str(e)}")  # Debug print
            raise Exception(f"Failed to read PDF: {str(e)}")
