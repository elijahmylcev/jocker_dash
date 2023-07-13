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
now = datetime.now()

# # App && Layout
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])


tab_1 = dash.html.Div([
    dash.html.H1('Рейтинг'),
    get_table(engine, start, end, now)
])
agents = get_agents('fos_user', engine)

Funnel = Funnel(
    text='Воронка продаж',
    engine=engine,
    agents=agents
)
KPI = KPI(
    text='Эффективность',
    engine=engine,
    agents=agents
)

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


@app.callback(
    [
        dash.Output('funnel', 'figure'),
        dash.Output('funnel_avg', 'figure')
    ],
    [
        dash.Input('funnel_agent', 'value'),
        dash.Input('date-picker-range', 'start_date'),
        dash.Input('date-picker-range', 'end_date')
    ]
)
def update_graph(agent, start_date, end_date):
    data = Funnel.calculate_funnel(agent=agent, start_date=start_date, end_date=end_date)
    data_avg = Funnel.get_avg_department(start_date=start_date, end_date=end_date)
    fig_funnel = go.Figure(data=[
        go.Funnel(
            y=[d["stage"] for d in data],
            x=[d["value"] for d in data]
        )
    ])
    fig_funnel.update_layout(
        plot_bgcolor='white',
        title="По агенту",
        margin={"l": 150, "r": 50, "t": 100, "b": 100}
    )

    fig_funnel_avg = go.Figure(data=[
        go.Funnel(
            y=[d["stage"] for d in data_avg],
            x=[d["value"] for d in data_avg]
        )
    ])
    fig_funnel_avg.update_layout(
        plot_bgcolor='white',
        title="По отделу",
        margin={"l": 150, "r": 50, "t": 100, "b": 100}
    )

    return fig_funnel, fig_funnel_avg


# @app.callback(
#     dash.Output('output-container', 'children'),
#     [dash.Input('date-picker-range', 'start_date'),
#      dash.Input('date-picker-range', 'end_date')])
# def update_output(start_date, end_date):
#     return f'Выбран промежуток: {start_date} до {end_date}'


@app.callback(
    [
        dash.Output('filtered-data', 'data'),
        dash.Output('selected-metrics', 'data'),
        dash.Output('selected-agents', 'data'),
        # dash.Output('kpi-table', 'data'),
        dash.Output('kpi_table', 'data'),
        dash.Output('kpi_average', 'children')
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
    if current_agent != selected_agents:
        kpi_average = KPI.get_kpi_average(selected_agents)
        kpi_table = KPI.get_table(selected_agents)
    else:
        kpi_table = KPI.table
        kpi_average = KPI.get_kpi_average(selected_agents)
    return filtered_df.to_json(orient='records'), list(columns), selected_agents, kpi_table.to_dict('records'), kpi_average


if __name__ == '__main__':
    app.run_server(debug=True)
