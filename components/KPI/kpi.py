import pandas as pd
import dash_core_components as dcc
import dash_html_components as html
from functions import get_agents
import dash_bootstrap_components as dbc
import plotly.express as px


class KPI:
    def __init__(self, text, engine, agent=13):
        self.text = text
        self.engine = engine
        self.df = None
        self.agent = agent

    def process(self):
        # df = self.execute_query(self.agent, 2022)
        self.df = pd.read_csv('components/KPI/KPI_result.csv')
        available_agents = get_agents('fos_user', self.engine)
        available_metrics = self.df.columns
        options_agents = [{
            'label': agent[1]['username'],
            'value': agent[1]['user_id']
        }
            for agent in available_agents.iterrows()]
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
                    options=[{'label': metric, 'value': metric} for metric in available_metrics],
                    value=available_metrics[4:7],
                    multi=True
                ),
            ]),
            dcc.Graph(id='kpi'),
        ])

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
