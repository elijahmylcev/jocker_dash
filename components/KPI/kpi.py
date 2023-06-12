import pandas as pd
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc


class KPI:
    def __init__(self, text):
        self.text = text

    def process(self):
        return html.Div([
                  html.H1(self.text)
                ])

    @staticmethod
    def get_query(month, year, id_agent):
        return f'''
            SELECT * FROM (
                SELECT 
                  {id_agent} AS id_agent, 
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
