import pandas as pd
from datetime import datetime
import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
from functions import get_df_from_table, get_agents, get_engine
from components import get_table, create_funnel, KPI

engine = get_engine()

# Time interval
start = datetime.strptime('2022-09-01', '%Y-%m-%d')
end = datetime.strptime('2022-09-30', '%Y-%m-%d')
now = datetime.now().strftime("%Y-%m-%d")
# print(f'start - {start}; \nend - {end} \nnow - {now}')

# # App && Layout
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])


tab_1 = html.Div([
  html.H1('Рейтинг'),
  get_table(engine, start, end, now)
])

tab_2 = create_funnel()
KPI = KPI('KPI', engine)

app.layout = html.Div([
  html.Div([
    html.Img(src='./static/logo.svg')
  ]),
  dcc.Tabs(id='tabs', value='tab-1', children=[
    dcc.Tab(label='Рейтинговая доска', value='tab-1', children=tab_1),
    dcc.Tab(label='Воронка продаж', value='tab-2', children=tab_2),
    dcc.Tab(label='KPI', value='tab-3', children=KPI.process()),
    dcc.Store(id='initial-data', data=KPI.df.to_json(orient='records'), storage_type='memory'),
    dcc.Store(id='filtered-data', storage_type='memory'),
    dcc.Store(id='selected-metrics', data=KPI.df.columns[3], storage_type='memory')
  ])
])


@app.callback(
    dash.Output('filtered-data', 'data'),
    dash.Input('agent-dropdown', 'value'),
    dash.State('initial-data', 'data')
)
def update_graph(selected_agents, initial_data):
    # Преобразование JSON-строки в исходный датафрейм
    initial_df = pd.read_json(initial_data, orient='records')
    # Фильтрация датафрейма по указанному идентификатору
    filtered_df = initial_df[initial_df['id_agent'] == selected_agents].copy()
    return filtered_df.to_json(orient='records')


# Callback-функция для обновления графика
@app.callback(
    dash.Output('kpi', 'figure'),
    dash.Input('filtered-data', 'data'),
    dash.State('selected_metrics', 'data')
)
def update_graph(data, selected_metrics):
    if data is None:
        # Если данные не доступны, отображаем пустой график
        return {}
    # Преобразование JSON-строки в фильтрованный датафрейм
    filtered_df = pd.read_json(data, orient='records')
    data = []
    for metric in selected_metrics:
        for column in KPI.df.columns:
            if column == metric:
                scatter = go.Scatter(
                    x=KPI.df['month'],
                    y=filtered_df[column],
                    mode='lines+markers',
                    name=metric
                )
                data.append(scatter)

    # Создание объекта Figure с использованием списка Scatter
    fig = go.Figure(data=data)

    # Настройка внешнего вида графика
    fig.update_layout(
        plot_bgcolor='white',
        showlegend=True,
        legend=dict(
            x=0,
            y=1
        ),
        hovermode='x'
    )

    return fig


@app.callback(
    dash.Output('filtered_data', 'data'),
    dash.Input('metric-dropdown', 'value'),
    dash.State('filtered_data', 'data')
)
def update_graph(selected_metrics):
    # Создание списка объектов Scatter для каждой выбранной метрики
    # data = []
    # for metric in selected_metrics:
    #     for column in KPI.df.columns:
    #         if column == metric:
    #             filtered_df = KPI.df[column]
    #             print(filtered_df)
    #             scatter = go.Scatter(
    #                 x=KPI.df['month'],
    #                 y=filtered_df,
    #                 mode='lines+markers',
    #                 name=metric
    #             )
    #             data.append(scatter)
    #
    # # Создание объекта Figure с использованием списка Scatter
    # fig = go.Figure(data=data)
    #
    # # Настройка внешнего вида графика
    # fig.update_layout(
    #     plot_bgcolor='white',
    #     showlegend=True,
    #     legend=dict(
    #         x=0,
    #         y=1
    #     ),
    #     hovermode='x'
    # )

    return selected_metrics


if __name__ == '__main__':
    app.run_server(debug=True)
