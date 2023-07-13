import pandas as pd
from dash import dash_table, dcc, html
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import plotly.express as px


class KPI:
    def __init__(self, text, engine, agents, agent=13):
        self.text = text
        self.engine = engine
        self.df = pd.read_csv('components/KPI/KPI_result.csv')
        self.agent = agent
        self.agents = agents
        self.average_metrics = None
        self.table = self.get_table(self.agent)

    def get_kpi_average(self, agent):
        if not agent:
            agent = self.agent
        scales = [
            'successful_deals',
            'assigned_tasks',
            'completed_tasks',
            'overdue_tasks_percentage',
            'profit',
            'average_deal_size'
        ]
        grouped_df = self.df.groupby('id_agent')[scales].mean().reset_index()
        grouped_df.fillna(0, inplace=True)
        result = []
        for scale in scales:

            fig = go.Figure()
            agent_value = grouped_df[grouped_df['id_agent'] == agent][scale].values
            fig.add_trace(
                go.Bar(
                    x=['Отдел', 'Агент'],
                    y=[
                        float(self.average_metrics[scale]),
                        float(agent_value[0] if len(agent_value) else 0)
                    ],
                    name='Department',
                    opacity=0.7,
                    marker=dict(color=['lightblue', 'lightgreen'])
                )
            )

            fig.update_layout(
                plot_bgcolor='white',
                title=None,
                title_x=None,
                xaxis_title="",
                yaxis_title="",
                legend=dict(x=.5, xanchor="center", orientation="h"),
                margin=dict(l=0, r=0, t=30, b=0)
            )

            graph = dcc.Graph(
                id=f'kpi_average_{scale}',
                figure=fig
            )

            # fig = dcc.Graph(
            #     id=f'kpi_average_{scale}',
            #     figure=px.bar(
            #             x=[scale, f'agent_{scale}'],
            #             y=[self.average_metrics[scale], len(scale)],
            #             # barmode='group',
            #     ).update_traces(
            #         marker={'line': {'width': 1}},
            #         xaoxis=None
            #     )
            # )
            result.append(
                dbc.Col([
                    html.P(f'{scale}'),
                    graph,
                ],
                    width=2
                )
            )
        result_layout = dbc.Row(children=result)
        return result_layout

    def process(self):
        # df = self.execute_query(self.agent, 2022)
        # self.df = pd.read_csv('components/KPI/KPI_result.csv')
        available_agents = self.agents
        self.get_average_metrics(metrics=['successful_deals',
                                          'profit',
                                          'average_deal_size',
                                          'assigned_tasks',
                                          'completed_tasks',
                                          'overdue_tasks_percentage'
                                          ])
        available_metrics = self.df.columns
        options_agents = [{
            'label': agent[1]['username'],
            'value': agent[1]['user_id']
        }
            for agent in available_agents.iterrows()]
        table = self.get_table(self.agent)
        return html.Div([
            html.H2(self.text, style={'text-align': 'center', 'margin-bottom': '20px'}),
            html.Div([
                html.Label('Выберите менеджера:'),
                dcc.Dropdown(
                    id='agent-dropdown',
                    options=options_agents,
                    value=options_agents[2]['value'],
                    multi=False
                ),
            ]),
            html.Div([
                html.Label('Выберите метрики:'),
                dcc.Dropdown(
                    id='metric-dropdown',
                    options=[{'label': metric, 'value': metric}
                             for metric in available_metrics
                             if metric not in ['calculate_date', 'id_agent', 'id_agent.1']
                             ],
                    value=[available_metrics[3]],
                    multi=True
                ),
            ]),
            dcc.Graph(id='kpi'),
            html.Div(
                id='kpi_average',
            ),
            dash_table.DataTable(
                id='kpi_table',
                columns=[{'name': i, 'id': i}
                         for i in table.columns
                         if i not in ['id_agent', 'id_agent.1']
                         ],
                data=table.to_dict('records'),
                sort_action='native',
                sort_mode='multi',
                style_cell={'textAlign': 'center'}
            )
        ])

    def get_average_metrics(self, metrics):
        self.average_metrics = self.df[[*metrics]].mean().round(2)

    def get_table(self, user_id):
        if user_id:
            table = self.df[self.df['id_agent'] == user_id]
            self.table = table
        else:
            table = None
        return table

    def execute_query(self, id_agent, year):
        """
        return result df in year
        :param id_agent: agent id
        :param year: year for analyse
        :return: df
        """
        dataframes = []
        for month in list(range(1, 13)):
            dataframes.append(pd.read_sql(self.get_query(month, year, id_agent), self.engine))
        result_df = pd.concat(dataframes)
        self.df = result_df
        return result_df

    @staticmethod
    def get_query(month, year, id_agent):
        return f'''
            SELECT * FROM (
                SELECT 
                  {id_agent} AS id_agent, 
                  {month} as month,
                  SUM(
                    CASE WHEN (
                      MONTH(complete_date) = {month} 
                      AND YEAR(complete_date) = {year} 
                      AND status = 6
                    ) THEN 1 ELSE 0 END
                  ) AS successful_deals, 
                  SUM(
                    CASE WHEN (
                      MONTH(complete_date) = {month} 
                      AND YEAR(complete_date) = {year} 
                      AND status = 6
                    ) THEN price ELSE 0 END
                  ) AS profit, 
                  ROUND(
                    (
                      SUM(
                        CASE WHEN (
                          MONTH(complete_date) = {month} 
                          AND YEAR(complete_date) = {year} 
                          AND status = 6
                        ) THEN price ELSE 0 END
                      ) / SUM(
                        CASE WHEN (
                          MONTH(complete_date) = {month} 
                          AND YEAR(complete_date) = {year} 
                          AND status = 6
                        ) THEN 1 ELSE 0 END
                      )
                    ), 
                    2
                  ) AS average_deal_size 
                FROM 
                  deals 
                WHERE 
                  user_id = {id_agent}
            ) AS x INNER JOIN (
                SELECT 
                  {id_agent} AS id_agent, 
                  SUM(
                    CASE WHEN (
                      MONTH(start) = {month} 
                      AND YEAR(start) = {year}
                    ) THEN 1 ELSE 0 END
                  ) AS assigned_tasks, 
                  SUM(
                    CASE WHEN (
                      complete_date 
                      AND MONTH(complete_date) = {month} 
                      AND YEAR(complete_date) = {year}
                    ) THEN 1 ELSE 0 END
                  ) AS completed_tasks, 
                  ROUND(
                    (
                      SUM(
                        CASE WHEN (complete_date > end) THEN 1 ELSE 0 END
                      ) / SUM(
                        CASE WHEN (
                          MONTH(start) = {month} 
                          AND YEAR(start) = {year}
                        ) THEN 1 ELSE 0 END
                      )
                    ), 
                    2
                  ) AS overdue_tasks_percentage 
                FROM 
                  tasks 
                WHERE 
                  worker_id = {id_agent}
            ) AS y
            on x.id_agent = y.id_agent
        '''
