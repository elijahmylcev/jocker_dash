import dash_table
from functions import get_rating_table

def get_table(engine, start, end, now):
  df = get_rating_table(engine, start, end, now)
  layout = dash_table.DataTable(
    id='table',
    columns=[{'name': i, 'id': i} for i in df.columns],
    data=df.to_dict('records'),
    sort_action='native',
    sort_mode='multi',
    style_cell={'textAlign': 'center'}
    )
  
  return layout
