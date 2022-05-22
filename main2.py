from run.agent import Agent
import seaborn as sns

import matplotlib.pyplot as plt
import numpy as np
from matplotlib import colors
from matplotlib.ticker import PercentFormatter

a = Agent(r'C:\Users\kbbudak\PycharmProjects\Charting\queries\prd.txt')
# a.draw_distplot("TOTALPRD",20)
#
# from scipy.stats import shapiro
#
cnc04 = a.df.loc[(a.df["WORKCENTER"] == "CNC-04") & (a.df["QUANTITY"] < 1250)]
cnc01 = a.df.loc[(a.df["WORKCENTER"] == "CNC-01") & (a.df["QUANTITY"] < 1250)]
#
# shapiro(cnc04["TOTALPRD"])
#
# sns.displot()

# fig, axs = plt.subplots(1, 2, sharey=True, tight_layout=True)
#
# # We can set the number of bins with the *bins* keyword argument.
# axs[0].hist(cnc04["TOTALPRD"], bins=55)


fig, axs = plt.subplots(1, 2, tight_layout=True)

# N is the count in each bin, bins is the lower-limit of the bin
N, bins, patches = axs[0].hist(cnc04["QUANTITY"], bins=55)

# We'll color code by height, but you could use any scalar
fracs = N / N.max()

# we need to normalize the data to 0..1 for the full range of the colormap
norm = colors.Normalize(fracs.min(), fracs.max())

# Now, we'll loop through our objects and set the color of each accordingly
for thisfrac, thispatch in zip(fracs, patches):
    color = plt.cm.viridis(norm(thisfrac))
    thispatch.set_facecolor(color)

# We can also normalize our inputs by the total number of counts
axs[0].hist(cnc04["QUANTITY"], bins=55, density=True)
axs[1].hist(cnc01["QUANTITY"], bins=55)
# Now we format the y-axis to display percentage
# axs[1].yaxis.set_major_formatter(PercentFormatter(xmax=1))

plt.show()