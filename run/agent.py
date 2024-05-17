import time
from config import server, username, password, database, database_iot, directory, project_directory,sleep_time
import pyodbc
import seaborn as sns
import pandas as pd
import datetime as dt
from dateutil.relativedelta import relativedelta
import os
import warnings
warnings.filterwarnings("ignore")

import plotly.graph_objects as go
import plotly.io as pio


def readquerry(queryx):
    queryy = queryx
    if queryy[0:6] == 'SELECT' or queryy[0:4] == 'WITH' \
            or queryy[0:4] == 'EXEC' or queryy[0:6] == 'INSERT' or queryy[0:6] == 'DELETE':
        return queryy
    else:
        if os.path.exists(queryy):
            text = open(queryy, 'r')
            queryy = text.read()
            text.close()
            return queryy

        else:
            raise Exception("Please enter correct directory or write SQL Query directly")


def parse_inserter_sql(table, columns, dbcolumns):
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
        self.connection = pyodbc.connect(
            f'DRIVER={{SQL Server}};SERVER={server};DATABASE={database};UID={username};PWD={password}')

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
                                time.sleep(sleep_time)  # wait for 1 second before trying again

                        else:
                            try:
                                cursor.execute(query, params)
                                return pd.DataFrame()
                            except pyodbc.Error as e:
                                if e == "No results.  Previous SQL was not a query.":
                                    print(f"An error occurred ({retry_count + 1}/{max_retries}): {e}")
                                    self.connection.commit()  # Make sure changes are committed if not a select query.
                                    return pd.DataFrame()
                                elif 'UNIQUE KEY constraint' in str(e):
                                    print("unique constraint")
                                    self.connection.commit()  # Make sure changes are committed if not a select query.
                                    return
                                print(f"An error occurred ({retry_count + 1}/{max_retries}): {e}")
                                retry_count += 1
                                time.sleep(sleep_time)  # wait for 1 second before trying again
                            self.connection.commit()

                        self.connection.commit()  # Make sure changes are committed if not a select query.

            except pyodbc.Error as e:
                print(f"An error occurred ({retry_count + 1}/{max_retries}): {e}")
                retry_count += 1
                time.sleep(sleep_time)  # wait for 1 second before trying again

        if retry_count == max_retries:
            print("Maximum number of retries reached. Could not connect to database.")

    def update_table(self, diro, table_name='', nullaccept=0, insert=0):
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

    def insert_into_db(self, diro, table_name, update=0):
        df = pd.read_excel(diro)
        final_output = ''
        for _, row in df.iterrows():
            values = ','.join([f"'{str(val)}'" for val in row])
            insert_query = f"INSERT INTO {table_name} VALUES ({values})"
            if update:
                with self.connection.cursor() as cursor:
                    cursor.execute(insert_query)
            else:
                final_output = final_output + insert_query + f"\n" + ';'

        return final_output

    def editandrun_query(self, textfile=project_directory + r"\Charting\queries\prdt_report_foryear_calculatıon.sql",
                         texttofind=["aaaa-bb-cc", "xxxx-yy-zz"],
                         texttoput=[str(dt.date(2022, 1, 1)), str(dt.date(2022, 1, 2))],
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

        retry_count = 0

        print(filedata)

        if return_string == 1:
            with self.connection.cursor() as cursor:
                while retry_count < 10:
                    try:
                        cursor.execute(filedata)
                        results = cursor.fetchall()
                        columns = [column[0] for column in cursor.description]
                        return pd.DataFrame.from_records(results, columns=columns)
                    except pyodbc.Error as e:
                        if 'No results. Previous SQL was not a query.' in str(e):
                            print("No Result from Query")
                            break
                        print(f"An error occurred ({retry_count + 1}/{10}): {e}")
                        retry_count += 1
                        time.sleep(sleep_time)

    def replace_and_insertinto(self, path=project_directory + r"\Charting\queries\HİSTORİCALSTOCKS.sql",
                               rapto=dt.date(2022, 9, 1), torep='xxxx-xx-xx'):
        with open(path, 'r') as file:
            filedata = file.read()
        for i in range(20):
            query = filedata.replace(torep, str(rapto))
            with self.connection.cursor() as cursor:
                cursor.execute(query)
            rapto += relativedelta(months=-1)

    def drop_table_if_exists(self, table_name):
        drop_stmt = f"IF OBJECT_ID('{table_name}', 'U') IS NOT NULL DROP TABLE {table_name};"
        with self.connection.cursor() as cursor:
            cursor.execute(drop_stmt)
            self.connection.commit()

    def create_table_from_df(self, df, table_name):
        self.drop_table_if_exists(table_name)  # Ensure the table doesn't exist
        sql_type_mapping = {
            'int64': 'INT',
            'float64': 'FLOAT',
            'object': 'VARCHAR(MAX)',  # Default for other types like strings
            'bool': 'BIT',
            'datetime64[ns]': 'DATETIME'
        }

        # Generate the column definitions using the mapping
        columns = []
        for col, dtype in df.dtypes.iteritems():
            sql_type = sql_type_mapping.get(str(dtype), 'VARCHAR(MAX)')
            columns.append(f"[{col}] {sql_type}")

        columns = ", ".join(columns)
        create_stmt = f"CREATE TABLE {table_name} ({columns});"

        with self.connection.cursor() as cursor:
            cursor.execute(create_stmt)
            self.connection.commit()

    def insert_data_from_df(self, df, table_name):
        placeholders = ", ".join("?" * len(df.columns))
        columns = ", ".join([f"[{col}]" for col in df.columns])
        insert_stmt = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"
        with self.connection.cursor() as cursor:
            for index, row in df.iterrows():
                cursor.execute(insert_stmt, tuple(row))
            self.connection.commit()

    # def correlation_matrix(self):
    #
    #     corr = self.df.corr()
    #     sns.set_theme(style="white")
    #     # Generate a mask for the upper triangle
    #     mask = np.triu(np.ones_like(corr, dtype=bool))
    #
    #     # Set up the matplotlib figure
    #     f, ax = plt.subplots(figsize=(11, 9))
    #
    #     # Generate a custom diverging colormap
    #     cmap = sns.diverging_palette(500, 220, as_cmap=True)
    #
    #     # Draw the heatmap with the mask and correct aspect ratio
    #     sns.heatmap(corr, mask=mask, cmap=cmap, vmax=.3, center=0,
    #                 square=True, linewidths=.5, cbar_kws={"shrink": .5})






    # def pie_multi_layer(self,df):
    #     fig = px.sunburst(df, names='names'  values='value')
    #     fig.show()


ag = Agent()


agiot = Agent(database=database_iot)


