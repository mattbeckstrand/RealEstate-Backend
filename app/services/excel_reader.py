import pandas as pd
import io

class ExcelTextExtractor:
    @staticmethod
    def readExcel(excelFile):
        try:
            # Read file content
            content = excelFile.file.read()
            
            # Create DataFrame
            df = pd.read_excel(io.BytesIO(content))
            
            important_text = []
            keywords = [
                'price', 'sqft', 'bedroom', 'bath', 'address',
                'property', 'type', 'year', 'built', 'lot',
                'garage', 'tax', 'zoning', 'value'
            ]
            
            # Convert DataFrame to text, focusing on important columns
            for column in df.columns:
                if any(keyword in column.lower() for keyword in keywords):
                    # Add column name and values
                    column_text = f"{column}:\n"
                    column_text += "\n".join(df[column].astype(str).tolist())
                    important_text.append(column_text)
            
            return important_text
            
        except Exception as e:
            print(f"Excel reading error: {str(e)}")
            raise Exception(f"Failed to read Excel: {str(e)}")
