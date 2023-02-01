import pandas as pd
from datetime import datetime
import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from functions import get_df_from_table, get_agents, get_engine
from components import get_table, create_funnel

engine = get_engine()

# Time interval
start = datetime.strptime('2023-01-01', '%Y-%m-%d')
end = datetime.strptime('2023-01-30', '%Y-%m-%d')
now = datetime.now().strftime("%Y-%m-%d")
print(f'start - {start}; \nend - {end} \nnow - {now}')

# App && Layout
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

tab_1 = html.Div([
  html.H1('Tab 1 Content'),
  get_table(engine, start, end, now)
])

tab_2 = create_funnel()

app.layout = html.Div([
  html.Div([
    html.Img(src='./static/logo.svg')
  ]),
  dcc.Tabs(id='tabs', value='tab-1', children=[
    dcc.Tab(label='Рейтинговая доска', value='tab-1', children=tab_1),
    dcc.Tab(label='Воронка продаж', value='tab-2', children=tab_2),
    dcc.Tab(label='Конверсия', value='tab-3', children=html.Div([
      html.H1('Tab 3 Content')
    ]))
  ])
])

if __name__ == '__main__':
  app.run_server(debug=True)
