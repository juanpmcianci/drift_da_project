#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Apr 24 17:31:37 2022

@author: juan
"""

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import tikzplotlib as tkz
pd.options.display.width = 0
users=pd.read_pickle('df_users.pkl')
#%%
users.describe
users['range_time']=users['range_time']/(3600*24)
#pie chart by trades
threshold=0.01
aux=users[(users['proportion_of_trades']>threshold)]
rest=aux['proportion_of_trades'].sum()
aux.append(aux.iloc[-1])
aux['proportion_of_trades'].iloc[-1]=1-rest
aux['uid'].iloc[-1]='all others'

sizes=aux['proportion_of_trades']
labels=aux['uid']
explode=np.zeros(len(aux))
explode[-1]=0.1
fig, ax = plt.subplots()

ax.pie(sizes, labels=labels, autopct='%1.1f%%', explode=explode, startangle=0)
ax.axis('equal')
plt.tight_layout()
plt.savefig('trades_by_prop.png')
plt.show()
aux.to_csv('tbp.csv',float_format='%.3f')
#pie chart by trades volume
threshold=0.01
aux=users[(users['proportion_of_trades_volume']>threshold)]
rest=aux['proportion_of_trades_volume'].sum()
aux.append(aux.iloc[-1])
aux['proportion_of_trades_volume'].iloc[-1]=1-rest
aux['uid'].iloc[-1]='all others'

sizes=aux['proportion_of_trades_volume']
labels=aux['uid']
explode=np.zeros(len(aux))
explode[-1]=0.1
fig, ax = plt.subplots()

ax.pie(sizes, labels=labels, autopct='%1.1f%%', explode=explode, startangle=0)
ax.axis('equal')
plt.tight_layout()
plt.savefig('trades_by_vol.png')

plt.show()

aux.to_csv('tbv.csv',float_format='%.3f')

#pie chart by arbs
threshold=0.70
aux=users[(users['prop_arbs']>threshold)]


