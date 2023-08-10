

class RatingBoard:
    def __init__(self, text, engine, agents):
        self.text = text
        self.engine = engine
        self.dataframe = None
        self.agents = agents

    def process(self):
        print('process')

if __name__ == '__main__':
    from functions import get_engine, get_agents
    engine = get_engine()
    agents = get_agents('fos_user', engine)
    rb = RatingBoard('RatingBoard', engine, agents)
    rb.process()
