from pprint import pprint
import pandas as pd
from dash import dcc, html
import copy
from datetime import datetime
import dash_bootstrap_components as dbc


class Funnel:
    def __init__(self, text, engine, agents, agent=13):
        self.text = text
        self.engine = engine
        self.dataframe = None
        self.agent = agent
        self.agents = agents
        self.conversion = None
        self.data = [
            {"stage": "Новый лид", "value": 1000, "status": [1, 8]},
            {"stage": "Первый контакт", "value": 800, "status": [2, 9]},
            {"stage": "Встреча состоялась", "value": 600, "status": [3]},
            {"stage": "Залог/Аванс/Бронь", "value": 400, "status": [5]},
            {"stage": "Ипотека открыта", "value": 200, "status": [4, 10]},
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

    def get_avg_department(self, start_date='2023-06-12', end_date='2023-07-12'):
        start_date = pd.to_datetime(start_date)
        end_date = pd.to_datetime(end_date)
        ids = self.get_deals_id()
        # if self.dataframe:
        result = self.dataframe[
            (self.dataframe['date_created'] >= start_date)
            & (self.dataframe['date_created'] <= end_date)
            & (self.dataframe['deal_id'].isin(ids))
        ]
        result = result \
            .groupby(['user_id', 'status']) \
            .size() \
            .reset_index(name='count')
        start_num_deals = result[result['status'].isin([1, 8])].groupby('user_id')['count'].sum()
        successful_deals = result[result['status'].isin([6, 12])].groupby('user_id')['count'].sum()
        self.conversion = (successful_deals / start_num_deals) * 100

        average_df = result.groupby('status')['count'].mean().reset_index()
        copied_data = copy.deepcopy(self.data)
        for item in copied_data:
            status = item.get('status', None)
            if status:
                filtered_row = average_df[(average_df['status'].isin(status))]
                count_value = filtered_row['count'].values
                count_value = count_value[0] if len(count_value) else 0
                item["value"] = round(count_value, 2)
        return copied_data

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
                if not filtered_row.empty and 'count' in filtered_row.columns:
                    count_value = filtered_row['count'].values[0]
                else:
                    count_value = 0
                item["value"] = count_value

        return self.data

    def get_leader_conversion(self, ):
        print(self.conversion)
        agent_min_conversion = self.conversion.idxmin() if len(self.conversion) else None
        agent_max_conversion = self.conversion.idxmax() if len(self.conversion) else None

        if agent_max_conversion and agent_min_conversion:
            print("Агент с минимальной конверсией:", agent_min_conversion)
            print("Агент с максимальной конверсией:", agent_max_conversion)
            conversion_min = self.conversion.loc[agent_min_conversion]
            conversion_max = self.conversion.loc[agent_max_conversion]
            agent_max_conversion_name = self.agents[self.agents['user_id'] == agent_max_conversion]['username'].values[0]
            agent_min_conversion_name = self.agents[self.agents['user_id'] == agent_min_conversion]['username'].values[0]
            children = [
                dbc.Alert(
                    f"Агент с минимальной конверсией: {agent_min_conversion_name} (Конверсия: {conversion_min:.2f}%)",
                    color="danger",
                    style={"margin": "10px"}
                ),
                dbc.Alert(
                    f"Агент с максимальной конверсией: {agent_max_conversion_name} (Конверсия: {conversion_max:.2f}%)",
                    color="success",
                    style={"margin": "10px"}
                )
            ]
        else:
            children = [
                dbc.Alert(
                    f"За указанный промежуток нет успешных сделок",
                    color="warning",
                    style={"margin": "10px"}
                )
            ]
        return children

    def process(self):
        df = self.execute_query()
        data = self.calculate_funnel()
        avg_data = self.get_avg_department()
        available_agents = self.agents
        options_agents = [{
            'label': agent[1]['username'],
            'value': agent[1]['user_id']
        } for agent in available_agents.iterrows()]
        return html.Div([
            html.H2(self.text, style={'text-align': 'center', 'margin-bottom': '20px'}),

            dbc.Row(children=[
                dbc.Col(children=[
                    html.Div([
                        html.Label('Выберите менеджера:'),
                        dcc.Dropdown(
                            id='funnel_agent',
                            options=options_agents,
                            value=options_agents[0]['value'],
                            multi=False
                        ),
                    ]),
                ], width=6),
                dbc.Col(children=[
                    html.Div([
                        html.Label('Выберите временной промежуток:'),
                        html.Br(),
                        dcc.DatePickerRange(
                            id='date-picker-range',
                            start_date=datetime(2023, 6, 1),
                            end_date=datetime.now(),
                            display_format='YYYY-MM-DD'
                        ),
                    ]),
                ], width=6)
            ]),
            html.Div(
                id='conversion_log',
            ),
            dbc.Row(children=[
                dbc.Col(children=[
                    dcc.Graph(
                        id='funnel',
                    ),
                ], width=6),
                dbc.Col(children=[
                    dcc.Graph(
                        id='funnel_avg',
                    ),
                ], width=6),
            ]),
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


if __name__ == '__main__':
    from functions import get_engine, get_agents
    engine = get_engine()
    agents = get_agents('fos_user', engine)
    funnel = Funnel(engine=engine, agents=agents, text='')
    funnel.process()
    funnel.get_avg_department()
