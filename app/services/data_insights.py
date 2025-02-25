import pandas as pd
from typing import Dict, Any

class DataInsights:
    def __init__(self, data: pd.DataFrame):
        self.data = data

    def analyze_rental_income(self) -> Dict[str, Any]:
        """Analyze rental income metrics from T12 data"""
        # Find rental income categories
        rental_categories = self.data[self.data['category'].str.contains('Rental|Rent|Income', case=False, na=False)]
        
        # Calculate monthly rent (average of the last 3 months for more recent data)
        monthly_columns = [f'month_{i}' for i in range(10, 13)]  # last 3 months
        monthly_rent = rental_categories[monthly_columns].sum().mean() if not rental_categories.empty else 0
        
        # Calculate annual rent based on total column
        annual_rent = rental_categories['total'].sum() if not rental_categories.empty else 0
        
        # Standard occupancy rate (could be calculated from actual data if available)
        occupancy_rate = 0.95
        
        # Effective gross income
        effective_gross_income = annual_rent * occupancy_rate
        
        return {
            "monthly_rent": round(float(monthly_rent), 2),
            "annual_rent": round(float(annual_rent), 2),
            "occupancy_rate": occupancy_rate,
            "effective_gross_income": round(float(effective_gross_income), 2)
        }