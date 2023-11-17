import time
from config import server,username,password,database,directory,project_directory
from matplotlib import colors
from config import directory
import plotly.express as px
import matplotlib.pyplot as plt
import pyodbc

import seaborn as sns
import pandas as pd
import numpy as np
import datetime as dt
from dateutil.relativedelta import relativedelta
import os
import warnings

warnings.filterwarnings("ignore")

import plotly.graph_objects as go
import plotly.io as pio


def readquerry(queryx):

    queryy = queryx
    if queryy[0:6] == 'SELECT' or queryy[0:4] == 'WITH'\
            or queryy[0:4] == 'EXEC' or queryy[0:6] == 'INSERT':
        return queryy
    else:
        if os.path.exists(queryy):
            text = open(queryy, 'r')
            queryy = text.read()
            text.close()
            return queryy

        else:
            raise Exception("Please enter correct directory or write SQL Query directly")


def parse_inserter_sql(table,columns,dbcolumns):
    a = pd.read_excel(r"C:\Users\kbbudak\Desktop\HURDA DURUŞLARI LİSTESİ.xlsx", sheet_name=r'bölüm bazlı hurda listesi')
    b = pd.read_excel(r"C:\Users\kbbudak\Desktop\HURDA DURUŞLARI LİSTESİ.xlsx", sheet_name=r'canias hurda listesi')
    c = a.merge(b, on="STEXT", how='inner')
    c = c[["SCRAPKEY", "DIVISION", "COSTCENTER", "CREATEDBY", "CREATEDAT", "CHANGEDBY", "CHANGEDAT"]]
    return c


class Agent:

    def __init__(self, server=server, database=database,
                 username=username, password=password):

        self.server = server
        self.database = database
        self.username = username
        self.password = password
        self.connection = pyodbc.connect(f'DRIVER={{SQL Server}};SERVER={server};DATABASE={database};UID={username};PWD={password}')

    # method returns the result of querry as dataframe.
    # dont accept unvalid query

    def run_query(self, query='', params=None, isselect=1):
        query = readquerry(query)
        max_retries = 10
        retry_count = 0
        print(query)
        while retry_count < max_retries:
            try:
                with self.connection.cursor() as cursor:
                    if isselect == 1:
                        if params is None:
                            cursor.execute(query)
                        else:
                            cursor.execute(query, params)
                        results = cursor.fetchall()
                        columns = [column[0] for column in cursor.description]
                        return pd.DataFrame.from_records(results, columns=columns)
                    else:
                        if params is None:
                            try:
                                cursor.execute(query)
                                return pd.DataFrame()
                            except pyodbc.Error as e:
                                print(f"An error occurred ({retry_count + 1}/{max_retries}): {e}")
                                retry_count += 1
                                time.sleep(1)  # wait for 1 second before trying again

                        else:
                            try:
                                cursor.execute(query, params)
                                return pd.DataFrame()
                            except pyodbc.Error as e:
                                if e == "No results.  Previous SQL was not a query.":
                                    print(f"An error occurred ({retry_count + 1}/{max_retries}): {e}")
                                    return pd.DataFrame()
                                elif 'UNIQUE KEY constraint' in str(e):
                                    print("unique constraint")
                                    return
                                print(f"An error occurred ({retry_count + 1}/{max_retries}): {e}")
                                retry_count += 1
                                time.sleep(1)  # wait for 1 second before trying again
                            self.connection.commit()

                        self.connection.commit()  # Make sure changes are committed if not a select query.

            except pyodbc.Error as e:
                print(f"An error occurred ({retry_count + 1}/{max_retries}): {e}")
                retry_count += 1
                time.sleep(1)  # wait for 1 second before trying again

        if retry_count == max_retries:
            print("Maximum number of retries reached. Could not connect to database.")

    def update_table(self, diro, table_name = '',nullaccept = 0,insert=0):
        df = pd.read_excel(diro)
        final_output = ''
        if table_name == '':
            raise ValueError("Tablo ismi belirtmediniz.")
        set_flag = 'SET_'
        where_flag = 'WHERE_'

        # Define the SQL update statement to use
        sql_query = f"UPDATE {table_name} SET "

        for row in df.index:
            for col in df.columns:
                # Check if the column has a SET flag
                if col.startswith(set_flag):
                    col_name = col[len(set_flag):]
                    value = df[col][row]
                    if nullaccept == 0:
                        if value is None:
                            continue
                    sql_query += f"{col_name} = '{value}',"
            sql_query = sql_query[:-1]
            sql_query = sql_query + ' '
            # Check if the column has a WHERE flag
            for col in df.columns:
                counter = 0
                if col.startswith(where_flag):
                    col_name = col[len(where_flag):]
                    value = df[col][row]
                    if nullaccept == 0:
                        if value is None:
                            continue
                    if counter == 1:
                        sql_query += f" AND  {col_name} = '{value}'"
                    else:
                        sql_query += f"WHERE {col_name} = '{value}'"
                        counter = 1
            print(sql_query)
            if insert:
                with self.connection.cursor() as cursor:
                    cursor.execute(sql_query)
            else:
                final_output = final_output + sql_query + f"\n" + ';'

            sql_query = f"UPDATE {table_name} SET "

        return final_output

    def insert_into_db(self,diro,table_name,update=0):
        df = pd.read_excel(diro)
        final_output = ''
        for _, row in df.iterrows():
            values = ','.join([f"'{str(val)}'" for val in row])
            insert_query = f"INSERT INTO {table_name} VALUES ({values})"
            if update:
                with self.connection.cursor() as cursor:
                    cursor.execute(insert_query)
            else:
                final_output = final_output  + insert_query + f"\n" +  ';'

        return final_output



    def editandrun_query(self,textfile=project_directory + r"\Charting\queries\prdt_report_foryear_calculatıon.sql",
                         texttofind=["aaaa-bb-cc", "xxxx-yy-zz"],texttoput=[str(dt.date(2022, 1, 1)),str(dt.date(2022, 1, 2))],
                         return_string=1):
        """This is a Python method called find_and_replace that takes in 3 parameters:

            - textfile (str): the file path of the text file that needs to be modified.
            - texttofind (str): the text that needs to be found and replaced in the text file.
            - texttoput (str): the text that needs to be replaced in the text file. """

        with open(textfile, 'r') as file:
            filedata = file.read()

        if type(texttofind) is not list or type(texttoput) is not list:
            raise Exception(r"Should give list of strings!")
        else:
            if len(texttofind) != len(texttoput):
                raise Exception(r"String list lengths must be same!")


        for i in range(len(texttoput)):
            filedata = filedata.replace(texttofind[i], texttoput[i])

        with open(project_directory + r"\Charting\queries\prdt_report_foryear_calculatıon_test.sql", 'w') as file:
            file.write(filedata)
        file.close()

        if return_string == 1:
            with self.connection.cursor() as cursor:
                return cursor.execute(filedata)



    def replace_and_insertinto(self,path = project_directory + r"\Charting\queries\HİSTORİCALSTOCKS.sql",
                               rapto=dt.date(2022, 9, 1),torep='xxxx-xx-xx'):
        with open(path, 'r') as file:
            filedata = file.read()
        for i in range(20):
            query = filedata.replace(torep, str(rapto))
            with self.connection.cursor() as cursor:
                cursor.execute(query)
            rapto += relativedelta(months=-1)


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



ag = Agent()
agiot = Agent(database="VALFSAN604T")
