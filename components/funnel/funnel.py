from pprint import pprint
import pandas as pd
from dash import dcc, html
from functions import get_agents
from dash import dash_table
import dash_bootstrap_components as dbc
import plotly.express as px


class Funnel:
    def __init__(self, text, engine, agent=13):
        self.text = text
        self.engine = engine
        self.dataframe = None
        self.agent = agent
        self.data = data = [
            {"stage": "Новый лид", "value": 1000, "status": [1, 8]},
            {"stage": "Первый контакт", "value": 800, "status": [2, 9]},
            {"stage": "Встреча состоялась", "value": 600, "status": [3]},
            {"stage": "Ипотека открыта", "value": 200, "status": [4, 10]},
            {"stage": "Залог/Аванс/Бронь", "value": 400, "status": [5]},
            {"stage": "Подписаний договоров", "value": 56, "status": [6, 12]},
          ]

    def get_deals_id(self, start_date='2023-06-12', end_date='2023-07-12'):
        start_date = pd.to_datetime(start_date)
        end_date = pd.to_datetime(end_date)

        result = self.dataframe[
            (self.dataframe['date_created'] >= start_date)
            & (self.dataframe['date_created'] <= end_date)
            & (self.dataframe['status'] == 1)
            ]

        result = result['deal_id'].to_list()
        return result

    def calculate_funnel(self, agent=None, start_date='2023-06-12', end_date='2023-07-12'):
        if not agent:
            agent = self.agent
        self.dataframe['date_created'] = pd.to_datetime(self.dataframe['date_created'])
        start_date = pd.to_datetime(start_date)
        end_date = pd.to_datetime(end_date)

        ids = self.get_deals_id()

        filtered_data = self.dataframe[
            (self.dataframe['date_created'] >= start_date)
            & (self.dataframe['date_created'] <= end_date)
            & (self.dataframe['deal_id'].isin(ids))
            & (self.dataframe['user_id'] == agent)
        ]

        # Расчет количества по показателям (статусу) для каждого пользователя
        result = filtered_data\
            .groupby(['user_id', 'status'])\
            .size()\
            .reset_index(name='count')

        for item in self.data:
            status = item.get('status', None)
            if status:
                filtered_row = result[(result['status'].isin(status))]
                count_value = filtered_row['count'].values[0]
                item["value"] = count_value

        return self.data

    def process(self):
        df = self.execute_query()
        data = self.calculate_funnel()
        available_agents = get_agents('fos_user', self.engine)
        options_agents = [{
            'label': agent[1]['username'],
            'value': agent[1]['user_id']
        } for agent in available_agents.iterrows()]
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
            dcc.Graph(id='funnel',
                figure={
                    "data": [
                        {
                          "type": "funnel",
                          "y": [d["stage"] for d in data],
                          "x": [d["value"] for d in data]
                        }
                    ],
                    "layout": {
                      "title": "Воронка продаж",
                      "margin": {"l": 50, "r": 50, "t": 100, "b": 100}
                    }
                }
            ),
        ])

    def execute_query(self):
        """
        return result df
        :return: df
        """
        self.dataframe = pd.read_sql(self.get_query(), self.engine)
        return self.dataframe

    @staticmethod
    def get_query():
        return '''
            SELECT 
                h.deal_id, 
                h.status,
                h.date_created,
                temp.user_id, 
                ds.title
            FROM deals_history h
            JOIN (
                SELECT id, user_id
                FROM deals d 
            ) as temp ON temp.id = h.deal_id
            JOIN deal_statuses ds on ds.id = h.status 
        '''


def create_funnel():
  data = [
    {"stage": "Новый лид", "value": 1000, "status": [1, 8]},
    {"stage": "Первый контакт", "value": 800, "status": [2, 9]},
    {"stage": "Встреча состоялась", "value": 600, "status": [3]},
    {"stage": "Ипотека открыта", "value": 200, "status": [4, 10]},
    {"stage": "Залог/Аванс/Бронь", "value": 400, "status": [5]},
    {"stage": "Подписаний договоров", "value": 56, "status": [6, 12]},
  ]
  layout = html.Div([
    dcc.Graph(
      id="funnel",

    )
  ])  
  return layout


if __name__ == '__main__':
    from functions import get_engine
    engine = get_engine()
    funnel = Funnel(engine=engine, text='')
    funnel.process()
    funnel.calculate_funnel()
