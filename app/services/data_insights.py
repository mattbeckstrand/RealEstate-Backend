import pandas as pd
from typing import Dict, Any

class DataInsights:
    def __init__(self, data: pd.DataFrame):
        self.data = data

    def analyze_rental_income(self) -> Dict[str, Any]:
        """Analyze rental income metrics from T12 data"""
        # Find the Total Rent Income row
        print('categories: ', self.data['category'])
        rent_row = self.data[self.data['category'] == 'Total Rental Income']
        
        if rent_row.empty:
            raise ValueError
        
        # Get annual rent from the 'total' column
        annual_rent = float(rent_row['total'].iloc[0])
        print('annual_rent: ', annual_rent)
        
        # Calculate monthly rent (annual rent divided by 12)
        monthly_rent = annual_rent / 12
        
        
        # Effective gross income
        
        return {
            "monthly_rent": round(monthly_rent, 2),
            "annual_rent": round(annual_rent, 2)
        }