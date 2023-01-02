from matplotlib import colors

from config import database
from config import username
from config import password
from config import server
from config import directory

import plotly.express as px
import matplotlib.pyplot as plt
import pyodbc
import seaborn as sns
import pandas as pd
import numpy as np
import os


import plotly.graph_objects as go
import plotly.io as pio

def readquerry(queryx):
    queryy = queryx

    if isinstance(queryy, pd.core.frame.DataFrame):
        return queryy
    elif queryy[0:6] == 'SELECT':
        return queryy
    else:
        if os.path.exists(queryy):
            text = open(queryy, 'r')
            queryy = text.read()
            text.close()
            return queryy

        else:
            raise Exception("Please enter correct directory or write SQL Query directly")


def change_line_of_text(textfile, linenum, dirofnewtext):
    a_file = open(textfile, "r")
    list_of_lines = a_file.readlines()

    b_file = open(dirofnewtext, "r")
    newtext = b_file.read()
    list_of_lines[linenum - 1] = newtext

    a_file = open(textfile, "w")
    a_file.writelines(list_of_lines)
    a_file.close()

def parse_wclist_querry(stand = "'CNCFREZE'"):
    query = "SELECT IASWORKCENT.WORKCENTER FROM IASWORKCENT \
LEFT OUTER JOIN IASWORKCENX ON (IASWORKCENX.CLIENT = IASWORKCENT.CLIENT \
AND IASWORKCENX.COMPANY = IASWORKCENT.COMPANY \
AND IASWORKCENX.PLANT = IASWORKCENT.PLANT \
AND IASWORKCENX.WORKCENTER = IASWORKCENT.WORKCENTER \
AND IASWORKCENX.LANGU = 'T') \
WHERE IASWORKCENT.CLIENT = '00' AND IASWORKCENT.ISDELETE = 0 AND IASWORKCENT.COMPANY = '01' \
AND IASWORKCENT.STAND = "
    query = query + stand
    return query



class Agent:

    def __init__(self, data_accses):
    
        self.df = data_accses
        
        if not isinstance(self.df, pd.core.frame.DataFrame):
            self.query = readquerry(data_accses)
            self.connection = pyodbc.connect('DRIVER={SQL Server};'
                                             'SERVER=' + server + ';DATABASE='
                                             + database + ';UID=' + username + ';PWD=' +
                                             password)
                                             
            self.cursor = self.connection.cursor()
            
            self.df = self.run_querry()


    # method returns the result of querry as dataframe.
    # dont accept unvalid query

    def run_querry(self,query=''):
        if query == '':
            query=self.query
        else:
            query = readquerry(query)
        return pd.read_sql(query, self.connection)

    # draw gannchart
    def draw_gannchart(self,df = '1', xx_start = "WORKSTART", xx_end = "WORKEND", xy = "WORKCENTER", xcolor = "PERSONELNUM",saveorshow = 'show', filename=None):

        if type(df) != pd.core.frame.DataFrame:
            fig = px.timeline(data_frame=self.df, x_start=xx_start, x_end=xx_end, y=xy, color=xcolor)
        else:
            fig = px.timeline(data_frame=df, x_start=xx_start, x_end=xx_end, y=xy, color=xcolor)



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

    def draw_bubblechart(self,df=None, saveorshow = 'show', filename = 'pic', col_list = [0,1,2,3,4]):
        """
        :param saveorshow: write 'save' if you want to keep as file or 'show' for just casting.
        :param filename: file name of the chart
        :param col_list: col xx: the axis of chart
                         col yy: the axis of chart
                         col widthofcirc: the diameter of bubbles
                         col colorof: another categorization
                         col item: bubbles
        """
        if df is not None:
            backup_df = self.df.copy()
            self.df = df

        cols = [val for val in list(self.df.columns)]

        fig = px.scatter(self.df, x=cols[0], y=cols[1],
                         size=cols[2], color=cols[3],
                         hover_name=cols[4], hover_data= ["WORKCENTER"],log_x=True,size_max=50,color_discrete_sequence=px.colors.qualitative.Alphabet,
                         width = 1500 , height=500)

        if saveorshow == 'show':
            self.df = backup_df
            return fig

        elif saveorshow == 'save':
            if not filename:
                self.df = backup_df
                raise Exception("Please enter file name for saving Scatter as a html file!!!")

            diroffile = os.path.join(directory, filename)

            if not os.path.exists(diroffile):
                fig.write_html(diroffile)
                if os.path.exists(diroffile):
                    self.df = backup_df
                    print("Scatter has been saved succesfully to directory entered.")

            else:
                self.df = backup_df
                raise Exception("There is already a file with same name")

        else:
            self.df = backup_df
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

    def draw_distrubiton_plot(self, workcenter, uplimit):

        # there will be auto-detect outliers code block!!!
        df_of_workcenter = self.df.loc[(self.df["WORKCENTER"] == workcenter) & (self.df["QUANTITY"] < uplimit)]
        # cnc01 = a.df.loc[(a.df["WORKCENTER"] == "CNC-01") & (a.df["QUANTITY"] < 1250)]
        #
        # shapiro(cnc04["TOTALPRD"])
        #
        # sns.displot()

        # fig, axs = plt.subplots(1, 2, sharey=True, tight_layout=True)
        #
        # # We can set the number of bins with the *bins* keyword argument.
        # axs[0].hist(cnc04["TOTALPRD"], bins=55)

        fig, axs = plt.subplots(1, tight_layout=True)

        # N is the count in each bin, bins is the lower-limit of the bin
        N, bins, patches = axs[0].hist(df_of_workcenter["QUANTITY"], bins=55)

        # We'll color code by height, but you could use any scalar
        fracs = N / N.max()

        # we need to normalize the data to 0..1 for the full range of the colormap
        norm = colors.Normalize(fracs.min(), fracs.max())

        # Now, we'll loop through our objects and set the color of each accordingly
        for thisfrac, thispatch in zip(fracs, patches):
            color = plt.cm.viridis(norm(thisfrac))
            thispatch.set_facecolor(color)

        # We can also normalize our inputs by the total number of counts
        axs[0].hist(df_of_workcenter["QUANTITY"], bins=55, density=True)
        # axs[1].hist(cnc01["QUANTITY"], bins=55)
        # Now we format the y-axis to display percentage
        # axs[1].yaxis.set_major_formatter(PercentFormatter(xmax=1))

        plt.show()




    # def pie_multi_layer(self,df):
    #     fig = px.sunburst(df, names='names'  values='value')
    #     fig.show()
