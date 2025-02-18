from typing import Dict, List, Union, Any
import pandas as pd
import numpy as np
import re

class DataCleaner:
    def __init__(self):
        self.category_mapping = {
            'Income': {
                'parent': None,
                'level': 0
            },
            'Rental Income': {
                'parent': 'Income',
                'level': 1
            },
            'Other Income': {
                'parent': 'Income',
                'level': 1
            },
            'Expenses': {
                'parent': None,
                'level': 0
            }
        }

    def clean_value(self, value: str) -> float:
        """Convert string values to float, handling currency and negative numbers."""
        if pd.isna(value) or value == '' or value == 'N/A':
            return 0.0
        
        # Remove currency symbols and commas
        value = str(value).replace('$', '').replace(',', '').strip()
        
        try:
            return float(value)
        except ValueError:
            return 0.0

    def identify_category_level(self, row_name: str) -> int:
        """Determine the hierarchical level of a category based on leading spaces."""
        leading_spaces = len(row_name) - len(row_name.lstrip())
        return leading_spaces // 2  # Assuming 2 spaces per level

    def clean_category_name(self, category: str) -> str:
        """Clean category names by removing account numbers and extra spaces."""
        # Remove account numbers (e.g., "6000 - ")
        category = re.sub(r'^\d+\s*-\s*', '', category)
        # Remove extra spaces
        category = ' '.join(category.split())
        return category.strip()

    def is_valid_row(self, row: pd.Series, monthly_values: Dict[str, float]) -> bool:
        """
        Check if a row contains valid data.
        Returns True if the row has a non-empty category and at least one non-zero value.
        """
        # Check if category is empty or just whitespace
        category = str(row.iloc[0]).strip()
        if not category or category == "N/A":
            return False

        # Skip rows that are just headers or metadata
        skip_keywords = [
            "Twelve Month Trailing",
            "Created on:",
            "Reporting Book:",
            "As of Date:",
            "Location:",
            "Statement",  # Added to catch header rows
            "Income Statement",  # Added to catch header rows
            "For the Period",  # Added to catch date range headers
        ]
        if any(keyword.lower() in category.lower() for keyword in skip_keywords):
            return False

        # Skip completely empty or white rows
        if all(pd.isna(val) or str(val).strip() == "" for val in row):
            return False

        # Skip rows where first column is empty or just spaces
        if not category or category.isspace():
            return False

        # Check if all values are zero
        return any(value != 0 for value in monthly_values.values())

    def process_t12_data(self, data: pd.DataFrame) -> pd.DataFrame:
        """Process T12 statement data into a clean, structured format."""
        # Remove header rows and empty columns
        data = data.dropna(how='all')
        data = data.dropna(axis=1, how='all')

        # Initialize clean data storage
        clean_data = []

        for idx, row in data.iterrows():
            category = row.iloc[0]  # First column contains categories
            if isinstance(category, str):
                # Process monthly values
                monthly_values = {}
                for col in range(1, 13):  # 12 months of data
                    if col < len(row):
                        monthly_values[f'month_{col}'] = self.clean_value(row.iloc[col])

                # Only process if row contains valid data
                if self.is_valid_row(row, monthly_values):
                    category_clean = self.clean_category_name(category)
                    level = self.identify_category_level(category)

                    clean_data.append({
                        'category': category_clean,
                        'level': level,
                        **monthly_values,
                        'total': self.clean_value(row.iloc[-1]) if len(row) > 13 else sum(monthly_values.values())
                    })

        return pd.DataFrame(clean_data) 