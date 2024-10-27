import pandas as pd
import json
import os


class BulkRandEngine:
      

  def handle_splitable(self, metadata, df):
    for key, value in metadata.items():
      if value.get("splitable"):
        sep = value.get("sep", ";")
        cols = value.get("cols")
        df[cols] = df[key].str.split(sep, expand=True)
        df.drop(columns=[key], inplace=True)
    return df

      

  def create_pandas_df(self, size, metadata):
    df_pandas = pd.DataFrame({key: value["method"](size, **value["parms"]) for key, value in metadata.items()})
    df_pandas = self.handle_splitable(metadata, df_pandas)
    return df_pandas
  
  @classmethod
  def convert_datetimes_to_string(self, pandas_df):
    for column in pandas_df.columns:
      if pandas_df[column].dtype == 'datetime64[ns]':
        pandas_df[column] = pandas_df[column].astype(str)
    return pandas_df
  

  @classmethod
  def create_streaming_df(self, pandas_df):
    pandas_df = self.convert_datetimes_to_string(pandas_df)
    list_of_dicts = pandas_df.to_dict('records')
    for record in list_of_dicts:
      yield json.dumps(record)

  @classmethod
  def create_streaming_series(self, pandas_series):
    for record in pandas_series:
      yield record

  @classmethod
  def create_file(path, word, limit_size):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w') as file:
      while file.tell() < limit_size:
        file.write(word + '\n')
    return True
  

  def microbatch_file_with_streaming(self, path, metadata, df_transformer, microbatch_size, total_size):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    while True:
      df = self.create_pandas_df(size=microbatch_size, metadata=metadata)
      df = df_transformer(df)
      df.to_csv(path, mode='a', header=False, index=False)
      if os.path.getsize(path) > total_size:
        break
      
if __name__ == '__main__':
  pass