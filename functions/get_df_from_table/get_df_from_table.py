import pandas as pd

def get_df_from_table(table_name: str, engine) -> pd.DataFrame:
  result_df = pd.read_sql(f'SELECT * FROM {table_name}', engine)
  return result_df