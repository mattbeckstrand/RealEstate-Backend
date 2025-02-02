import pandas as pd
from fastapi import UploadFile
from io import BytesIO
from typing import List
import numpy as np
from pandas import DataFrame

class ExcelTextExtractor:
    @staticmethod
    async def readExcel(file: UploadFile) -> DataFrame:
        """Read and extract text from Excel files."""
        try:
            # Read the file content
            contents = await file.read()
            file.file.seek(0)  # Reset file pointer for potential future reads
            
            # Read Excel file into pandas DataFrame
            df = pd.read_excel(BytesIO(contents))
            
            # Convert DataFrame to string representation
            df.columns = df.columns.str.strip().str.lower().str.replace(r'[^a-zA-Z0-9_]', '_')

            # Replace empty strings with NaN
            df = df.replace(r'^\s*$', np.nan, regex=True)

            # Drop rows and columns with too many missing values
            df = df.dropna(thresh=int(len(df.columns) * 0.5), axis=0)  # Drop rows with >50% missing values
            df = df.dropna(thresh=int(len(df) * 0.5), axis=1) 
            print(df.head())
            # Process each row
            
            # Join all parts with newlines
            return df
            
        except Exception as e:
            print(f"Error reading Excel file: {str(e)}")
            raise Exception(f"Failed to read Excel file: {str(e)}")

    @staticmethod
    def _process_rent_roll(df):
        """Process rent roll specific data"""
        try:
            text_parts = ["=== RENT ROLL ANALYSIS ==="]
            
            # Convert all columns to string and get their data
            for column in df.columns:
                values = df[column].dropna().astype(str).tolist()
                if values:
                    text_parts.append(f"{column}:\n{', '.join(values)}")
            
            # Try to calculate key metrics if possible
            try:
                if 'rent' in df.columns.str.lower().tolist():
                    rent_col = df.columns[df.columns.str.lower().str.contains('rent')][0]
                    total_rent = pd.to_numeric(df[rent_col], errors='coerce').sum()
                    text_parts.append(f"Total Rent: ${total_rent:,.2f}")
            except Exception as e:
                print(f"Error calculating rent metrics: {e}")
            
            return "\n\n".join(text_parts)
        except Exception as e:
            print(f"Error processing rent roll: {str(e)}")
            raise Exception(f"Failed to process rent roll: {str(e)}")

    @staticmethod
    def _process_financials(df):
        """Process financial document data"""
        try:
            text_parts = ["=== FINANCIAL ANALYSIS ==="]
            
            # Look for and process all numeric columns
            for column in df.columns:
                values = df[column].dropna()
                if pd.to_numeric(values, errors='coerce').notna().any():
                    # It's likely a numeric column
                    text_parts.append(f"{column}:\n{', '.join(values.astype(str).tolist())}")
                elif values.any():  # If there's any non-empty value
                    text_parts.append(f"{column}:\n{', '.join(values.astype(str).tolist())}")
            
            return "\n\n".join(text_parts)
        except Exception as e:
            print(f"Error processing financials: {str(e)}")
            raise Exception(f"Failed to process financials: {str(e)}")

    @staticmethod
    def _process_general_data(df):
        """Process general document data"""
        try:
            text_parts = ["=== GENERAL PROPERTY DATA ==="]
            
            # Process all columns
            for column in df.columns:
                values = df[column].dropna().astype(str).tolist()
                if values:
                    text_parts.append(f"{column}:\n{', '.join(values)}")
            
            return "\n\n".join(text_parts)
        except Exception as e:
            print(f"Error processing general data: {str(e)}")
            raise Exception(f"Failed to process general data: {str(e)}")
