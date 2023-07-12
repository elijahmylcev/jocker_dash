import pandas as pd
from functions import get_agents
from dash import dash_table, dcc, html
import dash_bootstrap_components as dbc
import plotly.express as px


class KPI:
    def __init__(self, text, engine, agent=13):
        self.text = text
        self.engine = engine
        self.df = pd.read_csv('components/KPI/KPI_result.csv')
        self.agent = agent
        self.average_metrics = None
        self.table = self.get_table(self.agent)

    def process(self):
        # df = self.execute_query(self.agent, 2022)
        # self.df = pd.read_csv('components/KPI/KPI_result.csv')
        available_agents = get_agents('fos_user', self.engine)
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
            html.H2(self.text, style={'text-align': 'center'}),
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
            html.Div(children=[
                dbc.Row([
                    dbc.Col(
                        dcc.Graph(id='kpi_average', figure=px.bar(
                            x=[
                                'successful_deals',
                                'assigned_tasks',
                                'completed_tasks',
                                'overdue_tasks_percentage'
                            ],
                            y=self.average_metrics[['successful_deals', 'assigned_tasks', 'completed_tasks', 'overdue_tasks_percentage']],
                            barmode='group'),
                            style={'backgroundColor': 'transparent'}
                        ),
                        width=6
                    ),
                    dbc.Col(
                        dcc.Graph(id='kpi_average_profit', figure=px.bar(
                            x=[
                               'profit',
                               'average_deal_size'
                            ],
                            y=self.average_metrics[['profit', 'average_deal_size']],
                            barmode='group')
                        ),
                        width=6
                    )
                ])
            ]),
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
        print(self.average_metrics)

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
