from functions import get_df_from_table


def get_agents(table_name, engine):
    df = get_df_from_table(table_name, engine)
    df_agents = df[
        df['roles'].str.contains('ROLE_AGENT')
        & df['position'].str.contains('ксперт по недвижимости')
    ][['id', 'username']]
    df_agents.rename(columns={'id': 'user_id'}, inplace=True)
    return df_agents
