from pypdf import PdfReader

class DataProcessor: 
    @staticmethod
    async def readPdf(pdfFile):
        reader = PdfReader(pdfFile)
        text = []
        for page in reader.pages:
            pageText = page.extract_text()
            text.append(pageText)
        return text
