import pandas as pd
from datetime import datetime
import dash
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
from functions import get_df_from_table, get_agents, get_engine
from components import get_table, Funnel, KPI

engine = get_engine()

# Time interval
start = datetime.strptime('2022-09-01', '%Y-%m-%d')
end = datetime.strptime('2022-09-30', '%Y-%m-%d')
now = datetime.now().strftime("%Y-%m-%d")

# # App && Layout
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])


tab_1 = dash.html.Div([
    dash.html.H1('Рейтинг'),
    get_table(engine, start, end, now)
])

Funnel = Funnel('Воронка продаж', engine)
KPI = KPI('KPI', engine)

app.layout = dash.html.Div([
    dash.html.Div([
        dash.html.Img(src='./static/logo.svg', style={'margin': '15px'})
    ]),
    dash.dcc.Tabs(id='tabs', value='tab-1', children=[
        dash.dcc.Tab(label='Рейтинговая доска', value='tab-1', children=tab_1),
        dash.dcc.Tab(label='Воронка продаж', value='tab-2', children=Funnel.process()),
        dash.dcc.Tab(label='KPI', value='tab-3', children=KPI.process()),
    ]),
    dash.dcc.Store(id='initial-data', data=KPI.df.to_json(orient='records'), storage_type='memory'),
    dash.dcc.Store(id='filtered-data', storage_type='memory'),
    dash.dcc.Store(id='selected-metrics', data=['profit'], storage_type='memory'),
    dash.dcc.Store(id='selected-agents', data=13, storage_type='memory'),
    # dash.dcc.Store(id='kpi-table', data=KPI.table.to_json(orient='records'), storage_type='memory')
])


# @app.callback(
#     dash.Output('filtered-data', 'data'),
#     dash.Output('selected-agent', 'data'),
#     dash.Input('agent-dropdown', 'value'),
#     dash.State('initial-data', 'data'),
#     dash.State('selected-metrics', 'data')
# )
# def update_agents(selected_agents, initial_data, selected_metrics):
#     print(selected_agents)
#     # Преобразование JSON-строки в исходный датафрейм
#     initial_df = pd.read_json(initial_data, orient='records')
#     # Фильтрация датафрейма по указанному идентификатору
#     filtered_df = initial_df[initial_df['id_agent'] == selected_agents].copy()
#     columns = ['month', 'year'] + selected_metrics
#     filtered_df = filtered_df[columns]
#     return filtered_df.to_json(orient='records'), selected_agents


# Callback-функция для обновления графика
@app.callback(
    dash.Output('kpi', 'figure'),
    dash.Input('filtered-data', 'data'),
)
def update_graph(data):
    if data is None:
        # Если данные не доступны, отображаем пустой график
        return {}
    # Преобразование JSON-строки в фильтрованный датафрейм
    filtered_df = pd.read_json(data, orient='records')
    data = []
    for metric in filtered_df.columns:
        if metric not in ['calculate_date', 'id_agent', 'id_agent.1']:
            scatter = go.Scatter(
                x=filtered_df['calculate_date'],
                y=filtered_df[metric],
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
        xaxis=dict(showgrid=True),
        yaxis=dict(showgrid=True),
        legend=dict(
            x=0,
            y=1
        ),
        hovermode='x'
    )

    return fig


# @app.callback(
#     dash.Output('kpi_table', 'figure'),
#     dash.Input('kpi-table', 'data'),
# )
# def update_graph(data):
#     table = pd.read_json(data, orient='records')
#     if data is None:
#         # Если данные не доступны, отображаем пустой график
#         return {}
#     return dash.dash_table.DataTable(
#                 id='kpi_table',
#                 columns=[{'name': i, 'id': i} for i in table.columns],
#                 data=table.to_dict('records'),
#                 sort_action='native',
#                 sort_mode='multi',
#                 style_cell={'textAlign': 'center'}
#             )

# Для реакции на изменение метрик
# @app.callback(
#     dash.Output('filtered-data', 'data'),
#     dash.Output('selected-metrics', 'data'),
#     dash.Input('metric-dropdown', 'value'),
#     dash.State('selected-agents', 'data'),
#     dash.State('initial-data', 'data')
# )
# def update_metrics(metric_dropdown, selected_agents, initial_data):
#     print(metric_dropdown)
#     # Преобразование JSON-строки в исходный датафрейм
#     initial_df = pd.read_json(initial_data, orient='records')
#     # Фильтрация датафрейма по указанному идентификатору
#     filtered_df = initial_df[initial_df['id_agent'] == selected_agents].copy()
#     columns = ['month', 'year'] + metric_dropdown
#     filtered_df = filtered_df[columns]
#     return filtered_df.to_json(orient='records'), metric_dropdown


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

    # return selected_metrics

@app.callback(
    [
        dash.Output('filtered-data', 'data'),
        dash.Output('selected-metrics', 'data'),
        dash.Output('selected-agents', 'data'),
        # dash.Output('kpi-table', 'data'),
        dash.Output('kpi_table', 'data')
    ],
    [
        dash.Input('agent-dropdown', 'value'),
        dash.Input('initial-data', 'data'),
        dash.Input('metric-dropdown', 'value'),
        # dash.State('kpi-table', 'data'),
        dash.State('selected-agents', 'data')
    ]
)
def update_data(selected_agents, initial_data, selected_metrics, current_agent):
    # Преобразование JSON-строки в исходный датафрейм
    initial_df = pd.read_json(initial_data, orient='records')
    # Фильтрация датафрейма по указанному идентификатору
    filtered_df = initial_df[initial_df['id_agent'] == selected_agents].copy()
    if selected_metrics is not None:
        columns = ['calculate_date'] + list(selected_metrics)
    else:
        columns = ['calculate_date']
    filtered_df = filtered_df[columns]
    print(current_agent, selected_agents)
    if current_agent != selected_agents:
        kpi_table = KPI.get_table(selected_agents)
        print(kpi_table)
    else:
        kpi_table = KPI.table
    return filtered_df.to_json(orient='records'), list(columns), selected_agents, kpi_table.to_dict('records')


if __name__ == '__main__':
    app.run_server(debug=True)
