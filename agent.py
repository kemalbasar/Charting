from config import database
from config import username
from config import password
from config import server
from config import directory


import plotly.express as px
import pyodbc
import pandas as pd
import os

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
    def draw_gannchart(self, data_source, saveorshow, xx_start, xx_end, xy, xcolor,filename=None):

        if isinstance(data_source, pd.core.frame.DataFrame):
            print("Dataframe is ready")
        elif isinstance(data_source, str):
            data_source = self.run_querry(data_source)
            print("Dataframe is ready")
        else:
            raise Exception("You should enter dataframe or SQL Querry")

        fig = px.timeline(data_source, x_start=xx_start, x_end=xx_end, y=xy, color=xcolor)

        if saveorshow == 'show':
            fig.show()

        elif saveorshow == 'save':
            if filename == None:
                raise Exception("Please enter file name for saving GannChart as a html file!!!")

            diroffile = os.path.join(directory, filename)

            if not os.path.exists(diroffile):
                fig.write_html(diroffile)
                if os.path.exists(diroffile):
                    print("GannChart has been saved succesfully to directory entered.")

            else:
                raise Exception("There is already a file with same name")

        else:
            raise Exception("Please write 'save or 'show' !!")
