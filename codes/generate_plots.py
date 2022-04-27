#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
This file generates the plots from the report
@author: juan
"""

#checks if we need to work with datasets
from os.path import exists
from datetime import datetime 
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from load_data import load_drift_data
from gets_trades import format_drift_dataset
from generate_user_df import generate_user_dataframe
from time_series import generate_tsa
PATH_TRADES='trades.pkl'
PATH_USERS='users.pkl'
ALPHA=0 #criterion for arbitrage
#tests if files exist
if  exists(PATH_TRADES):
    trades=pd.read_pickle(PATH_TRADES)
else:
    trades=load_drift_data()
    trades=format_drift_dataset(trades,alpha=ALPHA,SAVEPATH=PATH_TRADES)

if exists(PATH_USERS):
    users=pd.read_pickle(PATH_USERS)
else:
    users=generate_user_dataframe(trades,SAVEPATH=PATH_USERS)

# generates plots for the general trades:


td=trades['time_diff']
total_longs=trades['totalLongs']
total_shorts=trades['totalShorts']
arb=trades['arb']

SECONDS_IN_A_DAY=3600*24
total_time=np.cumsum(td)/SECONDS_IN_A_DAY

# plots time difference    

plt.plot(total_time,td)
plt.title('time differences')
plt.ylabel('seconds')
plt.xlabel('days')
plt.tight_layout()
plt.savefig('time_diff_vs_time.png')
plt.show()
plt.plot(total_time,total_longs/total_shorts,label='total longs/total shorts')
plt.plot(total_time,np.ones(len(total_longs)),'--',label='longs=shorts')
plt.legend()
plt.xlabel('days')
plt.title('longs-to-shorts ratio')
plt.tight_layout()
plt.savefig('lts.png')
plt.show()
labels = 'Arbitrage','non-arbitrage'
explode = (0.1, 0.1)  # only "explode" the 2nd slice (i.e. 'Hogs')


arb_prop=np.sum(arb==1)/len(arb)
nonarb_prop=1-arb_prop

fig1, ax1 = plt.subplots()
ax1.pie([arb_prop,nonarb_prop], explode=explode, labels=labels, autopct='%1.1f%%',
        shadow=True, startangle=90)
ax1.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
plt.tight_layout()
plt.savefig('pie_arb00.png')
plt.show()

labels = 'Mark above oracle','Mark below oracle'
explode = (0.1, 0.1)  # only "explode" the 2nd slice (i.e. 'Hogs')


above=np.sum(trades['markPriceBefore']>trades['oraclePrice'])/len(arb)
below=1-above

fig1, ax1 = plt.subplots()
ax1.pie([above,below], explode=explode, labels=labels, autopct='%1.1f%%',
        shadow=True, startangle=90)
ax1.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
plt.tight_layout()
plt.savefig('pie_mark_oracle.png')
plt.show()

# Plots mark vs oracle
plt.title('Oracle and Mark')
plt.plot(total_time,trades['oraclePrice'],label='Oracle')
plt.xlabel('days')
plt.plot(total_time,trades['markPriceBefore'],label='mark')
plt.ylabel('(USD)')
plt.legend()
plt.tight_layout()
plt.savefig('oracle_vs_mark.png')
plt.show()
plt.title('Oracle - mark')
plt.plot(total_time,100*(trades['oraclePrice']-trades['markPriceBefore'])/trades['oraclePrice'])
plt.ylabel('% ')
plt.tight_layout()
plt.savefig('oracle_minus_mark.png')
plt.show()
plt.title('Histogram oracle - mark')
plt.hist(100*(trades['oraclePrice']-trades['markPriceBefore'])/trades['oraclePrice'],bins=100,density=True)
plt.xlabel(r'$\rho$')
plt.xlim([-2,2])
plt.tight_layout()
plt.savefig('oracle_minus_mark_hist.png')
plt.show()

#Plots log density of transaction amount. This is done so that it is easier to visualise
plt.hist(np.log(trades['quoteAssetAmount']),density=True,bins=70)
plt.ylabel('density')
plt.xlabel(r'$\log(x)$')
plt.title('log quote asset amount')
plt.savefig('hist_quote_asset.png')
plt.show()

plt.hist(np.log(trades['time_diff'][trades['time_diff']>1e-3]),density=True,bins=50)
plt.xlabel(r'$\log(\Delta t)$')
plt.title('log time difference')
plt.savefig('hist_time_diff.png')
plt.show()
# plots some histograms
plt.plot(total_time,np.log(trades['time_diff']))
plt.ylabel(r'$\log(\Delta t)$')
plt.xlabel('days')
plt.title('log time difference')
plt.tight_layout()
plt.savefig('dtvst.png')
plt.show()

plt.plot(total_time,np.log(trades['quoteAssetAmount']))
plt.ylabel(r'$\log(x)$')
plt.xlabel('days')
plt.title('log quote price')
plt.tight_layout()
plt.savefig('dxvst.png')
plt.show()


# deals with users stuff

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

# does the time series part
times=trades['humanTime']
skip=100
#time series for oracle:
m_oracle,fig_fore_oracle,fig_com_oracle=generate_tsa(times,trades['oraclePrice'],skip=skip,SAVENAME='oracle',TITLE='oracle')
#time series for diff:
m_diff,fig_fore_diff,fig_com_diff=generate_tsa(times,trades['oraclePrice']-trades['markPrice'],skip=skip,SAVENAME='difference',TITLE='difference')
#time series for mark:
m_mark,fig_fore_mark,fig_com_mark=generate_tsa(times,trades['markPrice'],skip=skip,SAVENAME='mark',TITLE='mark')
