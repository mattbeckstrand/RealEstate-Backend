import pandas as pd

class DataInsights:
    def __init__(self, data: pd.DataFrame):
        self.data = data

    def t12TrailingFinancials(self):
        gpi = self.data["Total Rental Income"].sum() if "Total Rental Income" in self.data.rows else 0
        return gpi