from config import dirofquery
from run.agent import Agent
from run.agent import readtext
import seaborn as sns

a = Agent(dirofquery)
a.df.describe()
a.df['FAILURETEXT'].value_counts()
# drop rows having nones.
adropped = a.df.dropna
# dropping outliers.
a.df = a.df.loc[a.df["FAILURETIME"] < 200]
sns.displot(a.df, x="FAILURETIME", bins=100)
a.draw_bubblechart("save", "FAILURETIME", "DISPLAY", "FAILURETIME", "FAILURETEXT", "MATERIAL", "bubblechart1")
# group by
a.df.groupby(["DISPLAY"]).mean()
# sort
asorted = a.df.sort_values(by='FAILURETIME')
# nontype datas
a.df[a.df.isnull().any(axis=1)].head()

a.df.dropna()  # Drop missing observations
a.df.dropna(how='all')  # Drop observations where all cells is NA
a.df.dropna(axis=1, how='all')  # Drop column if all the values are missing
a.df.dropna(thresh=5)  # Drop rows that contain less than 5 non-missing values
a.df.fillna(0)  # Replace missing values with zeros
a.df.isnull()  # returns True if the value is missing
a.df.notnull()
