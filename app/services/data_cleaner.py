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

    def is_valid_row(self, row: pd.Series, category: str) -> bool:
        """
        Check if a row contains meaningful data.
        Returns False for rows that are empty, contain only zeros, or are header/metadata rows.
        """
        if not isinstance(category, str) or not category.strip():
            return False

        # Skip header/metadata rows
        skip_patterns = [
            'Twelve Month Trailing',
            'Created on',
            'Reporting Book',
            'As of Date',
            'Location',
        ]
        if any(pattern in category for pattern in skip_patterns):
            return False

        # Check if all numeric values in the row are zero
        numeric_values = [self.clean_value(val) for val in row[1:] if pd.notna(val)]
        if not numeric_values or all(val == 0 for val in numeric_values):
            return False

        return True

    def process_t12_data(self, data: pd.DataFrame) -> pd.DataFrame:
        """Process T12 statement data into a clean, structured format."""
        # Remove header rows and empty columns
        data = data.dropna(how='all')
        data = data.dropna(axis=1, how='all')

        # Initialize clean data storage
        clean_data = []

        for idx, row in data.iterrows():
            category = row.iloc[0]  # First column contains categories
            
            # Skip invalid or empty rows
            if not self.is_valid_row(row, category):
                continue

            category_clean = self.clean_category_name(category)
            level = self.identify_category_level(category)

            # Process monthly values
            monthly_values = {}
            for col in range(1, 13):  # 12 months of data
                if col < len(row):
                    monthly_values[f'month_{col}'] = self.clean_value(row.iloc[col])

            if monthly_values:  # Only add if we have values
                clean_data.append({
                    'category': category_clean,
                    'level': level,
                    **monthly_values,
                    'total': self.clean_value(row.iloc[-1]) if len(row) > 13 else sum(monthly_values.values())
                })

        return pd.DataFrame(clean_data)