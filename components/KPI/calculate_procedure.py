import pandas as pd
from datetime import datetime
from tqdm import tqdm
import calendar
from sqlalchemy import text
from functions import get_engine
from dateutil.relativedelta import relativedelta


class CalculateKPI:
    """
    Class for calculate statistic
    """
    def __init__(self, output_file, engine):
        self.now_month = datetime.now().month
        self.now_year = datetime.now().year
        self.out = output_file
        self.engine = engine
        self.users = self.get_unique_users()
        self.date_range = self.get_range()

    def process(self) -> None:
        df_list = []
        for _date in tqdm(self.date_range.keys(), desc='Processing Dates'):
            list_agents = self.engine.execute(f'SELECT id FROM fos_user WHERE created_at < DATE("{_date}")').fetchall()
            list_agents = [agent[0] for agent in list_agents]
            for user in list_agents:
                _, last_day = calendar.monthrange(_date.year, _date.month)
                date_c = datetime(_date.year, _date.month, last_day).strftime('%Y-%m-%d')
                query = self.get_request(_date.month, _date.year, user)
                df = pd.read_sql(query, self.engine)
                df['calculate_date'] = date_c
                df_list.append(df)
        df = pd.concat(df_list)
        try:
            df.to_csv(self.out, index=False)
        except Exception as e:
            print(str(e))

    def get_start(self) -> datetime:
        query = text("SELECT MIN(created_at) AS earliest_date FROM deals;")
        result = self.engine.execute(query)
        earliest_date = result.scalar()
        return earliest_date

    def get_unique_users(self) -> list:
        query = text("SELECT distinct user_id from deals;")
        result = self.engine.execute(query)
        users = [row[0] for row in result.fetchall()]
        filtered_users = list(filter(lambda x: x is not None, users))
        return filtered_users

    def get_range(self) -> dict:
        """

        :return: Массив дат от старта до предыдущего месяца с шагом 1 месяц
        """
        end_date = datetime.now() - relativedelta(months=1)
        date_range = {}
        current_date = self.get_start()
        while current_date < end_date:
            date_range[current_date] = []
            current_date += relativedelta(months=1)
        return date_range

    @staticmethod
    def get_request(month, year, id_agent) -> str:
        return f'''
            SELECT * FROM (
                SELECT 
                  {id_agent} AS id_agent, 
                  {0} as calculate_date,
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


if __name__ == '__main__':
    date = CalculateKPI(output_file='KPI_result.csv', engine=get_engine())
    date.process()
