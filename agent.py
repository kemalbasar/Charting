from config import database
from config import username
from config import password
from config import server

import plotly.express as px
import pyodbc
import pandas as pd

#import matplotlib
#import sqlalchemy as sa


class Agent:

    def __init__(self):
        self.connection = pyodbc.connect('DRIVER={SQL Server};SERVER='+server+';DATABASE='+database+';UID='+username+';PWD='+ password)
        self.cursor = self.connection.cursor()
        #self.query = query
        #query = "SELECT * FROM IASPRDBARKOD;"

    #method returns the result of querry as dataframe.
    #dont accept unvalid query
    def run_querry(self, query):

        return pd.read_sql(query, self.connection)

    #draw gannchart
    def draw_gannchart(self, data_source, xx_start, xx_end, xy, xcolor):

        if isinstance(data_source, pd.core.frame.DataFrame):
            print("Dataframe is ready")
        elif isinstance(data_source, str):
            data_source = self.run_querry(data_source)
            print("Dataframe is ready")
        else:
            raise Exception("You should enter dataframe or SQL Querry")

        fig = px.timeline(data_source, x_start=xx_start, x_end=xx_end, y=xy, color=xcolor)
        fig.show()
