from config import database
from config import username
from config import password
from config import server
from config import directory

import plotly.express as px
import matplotlib.pyplot as plt
# import pyodbc
import seaborn as sns
import pandas as pd
import numpy as np
import os


def readquerry(queryx):
    queryy = queryx

    if isinstance(queryy, pd.core.frame.DataFrame):
        return queryy
    elif queryy[0:5] == 'SELECT':
        return queryy
    else:
        if os.path.exists(queryy):
            text = open(queryy, 'r')
            queryy = text.read()
            text.close()
            return queryy

        else:
            raise Exception("Please enter correct directory or write SQL Query directly")

def change_line_of_text(textfile,linenum,dirofnewtext):

    a_file = open(textfile, "r")
    list_of_lines = a_file.readlines()

    b_file = open(dirofnewtext, "r")
    newtext = b_file.read()
    list_of_lines[linenum-1] = newtext

    a_file = open(textfile, "w")
    a_file.writelines(list_of_lines)
    a_file.close()


class Agent:

    def __init__(self, query):
        self.query = readquerry(query)
        self.df = self.run_querry()
        if not isinstance(self.df, pd.core.frame.DataFrame):
            self.connection = pyodbc.connect('DRIVER={SQL Server};'
                                         'SERVER=' + server + ';DATABASE=' + database + ';UID=' + username + ';PWD=' +
                                         password)
            self.cursor = self.connection.cursor()
        self.query = readquerry(query)
        self.df = self.run_querry()

        # self.query = query
        # query = "SELECT * FROM IASPRDBARKOD;"

    # method returns the result of querry as dataframe.
    # dont accept unvalid query

    def run_querry(self):

        if isinstance(self.query, pd.core.frame.DataFrame):
            print("Dataframe is ready")
            print(self.query)
            return self.query

        elif isinstance(self.query, str):
            return pd.read_sql(self.query, self.connection)

        else:
            raise Exception("You should enter dataframe or SQL Querry")

    # draw gannchart
    def draw_gannchart(self, saveorshow, xx_start, xx_end, xy, xcolor, filename=None):

        fig = px.timeline(self.df, x_start=xx_start, x_end=xx_end, y=xy, color=xcolor)

        if saveorshow == 'show':
            fig.show()

        elif saveorshow == 'save':
            if not filename:
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

    def draw_bubblechart(self, saveorshow, xx, yy, widthofcirc, colorof, item, filename=None):
        """
        :param saveorshow: write 'save' if you want to keep as file or 'show' for just casting.
        :param filename: file name of the chart
        :param xx: the axis of chart
        :param yy: the axis of chart
        :param widthofcirc: the diameter of bubbles
        :param colorof: another categorization
        :param item: bubbles
        """

        fig = px.scatter(self.df, x=xx, y=yy,
                         size=widthofcirc, color=colorof,
                         hover_name=item, log_x=True)

        if saveorshow == 'show':
            fig.show()

        elif saveorshow == 'save':
            if not filename:
                raise Exception("Please enter file name for saving Scatter as a html file!!!")

            diroffile = os.path.join(directory, filename)

            if not os.path.exists(diroffile):
                fig.write_html(diroffile)
                if os.path.exists(diroffile):
                    print("Scatter has been saved succesfully to directory entered.")

            else:
                raise Exception("There is already a file with same name")

        else:
            raise Exception("Please write 'save or 'show' !!")

    def correlation_matrix(self):

        corr = self.df.corr()
        sns.set_theme(style="white")
        # Generate a mask for the upper triangle
        mask = np.triu(np.ones_like(corr, dtype=bool))

        # Set up the matplotlib figure
        f, ax = plt.subplots(figsize=(11, 9))

        # Generate a custom diverging colormap
        cmap = sns.diverging_palette(500, 220, as_cmap=True)

        # Draw the heatmap with the mask and correct aspect ratio
        sns.heatmap(corr, mask=mask, cmap=cmap, vmax=.3, center=0,
                    square=True, linewidths=.5, cbar_kws={"shrink": .5})
