import pandas as pd

class DataFrameMerger:
    def __init__(self, df1, df2, key_left, key_right)->None:
        self.df1 = df1
        self.df2 = df2
        self.key_left = key_left
        self.key_right = key_right

    def table(self)->pd.DataFrame:
        return pd.merge(self.df1.table(), self.df2.table(), left_on=self.key_left, right_on=self.key_right)
