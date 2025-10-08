import numpy as np
from random import randint


class Changer:

    def __init__(self, cols_to_change):
        self.cols_to_change = cols_to_change

    def __transformer_numeric(self, df):
        numeric_types = ['int64', 'int32', 'float32', 'float64']
        for col in df.columns:
            if col in self.cols_to_change and df[col].dtype in numeric_types:
                np.random.seed(None)
                df[col + '_random'] = np.random.randint(df[col].min(), df[col].max(), size=len(df))
                df[col + '_random_signal'] = np.random.choice([-1, 1], size=len(df))
                df[col + '_random'] = df[col + '_random'] * df[col + '_random_signal']
                df[col] = df[col] + df[col + '_random']
                df.drop(columns=[col + '_random', col + '_random_signal'], inplace=True)
        return df


    def __transformer_object(self, df):
        for col in df.columns:
            if col in self.cols_to_change and df[col].dtype == 'object':
                df[col] = np.roll(df[col], randint(1, len(df)))
        return df

    def updater(self, df):
        transformers = [self.__transformer_numeric, self.__transformer_object]
        for transform in transformers:
            df = transform(df)
        return df