#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Apr 20 08:08:22 2022

Here we create a script with the transactions per user

@author: juan
"""

from datetime import datetime 
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from load_data import load_drift_data
from gets_trades import format_drift_dataset


def generate_user_dataframe(trades,SAVEPATH=None):
    '''
    Here we format the drift trade dataset for our purposes

    Parameters
    ----------
    trades : Pandas dataframe
        dataframe containing the drift dataset info. THIS SHOULD BE THE ONE FROM FORMAT_DRIFT_DATASET

    SAVEPATH: str where to save a .pkl with the data. PLSEASE INCLUDE EXTENSION

    Returns
    -------
    users: Pandas dataframe containing the following info on each trader
    '''

    # finds  number of transactions per user
    def get_stats_per_user(df0,user,uid):
        total_trx=len(df0)
        df=df0[df0['user']==user]
        descr=df.describe()
        dst=descr['serverTimestamp']
        dsa=descr['quoteAssetAmount']
        total_volume=np.sum(df0['quoteAssetAmount'])
        vt=np.sum(df['quoteAssetAmount'])
        direction=df['direction'],
        t0=pd.to_datetime(dst['min'],unit='ms')
        # import pdb
        # pdb.set_trace()
        nt=int(dst['count'])
        now=pd.to_datetime(datetime.today().now())
        if nt>1:
            tf=pd.to_datetime(dst['max'],unit='ms')
        else:
            tf=now
        range_time_h=(tf-t0)
        range_time=range_time_h.total_seconds()
        arb=np.zeros(nt)
        for i in range(nt):
            if (trades['markPriceBefore'].iloc[i]<trades['oraclePrice'].iloc[i]) and trades['direction'].iloc[i]=='Long':
                arb[i]=1
            if (trades['markPriceBefore'].iloc[i]>trades['oraclePrice'].iloc[i]) and trades['direction'].iloc[i]=='Short':
                arb[i]=1
        total_liqs=df['liquidation'].sum()
        liqs=df['liquidation']
        indx=[]
        if total_liqs>0:
            for i in range(len(liqs)):
                if liqs.iloc[i]==True:
                    indx.append(i)
            last_liquidation=df['humanTime'].iloc[indx[-1]]
            time_liq_aux=tf-last_liquidation
            if time_liq_aux.total_seconds()>0:
                came_back=True
            else:
                came_back=False
        else:
            came_back=None
        
        total_shorts=np.sum(df['direction']=='Short')
        total_longs=np.sum(df['direction']=='Long')
    
        
        output={
           "uid":uid,
           "user":user,
           "t0":t0,
           "tf":tf,
           'range_time':range_time,
           'range_time_h':range_time_h,
           "seconds_per_trx":range_time/nt,
           "mean_amount":dsa['mean'],
           "min_amount":dsa['min'],
           "max_amount":dsa['max'],
           "proportion_of_trades":nt/total_trx,
           "proportion_of_trades_volume":np.sum(df['quoteAssetAmount'])/total_volume,
           "direction":direction,
           "arbs":arb,
           "prop_arbs":np.sum(arb)/nt,
           "trx":nt,
           'vol':vt,
           "liqs":df['liquidation'].sum(),
           "came_back":came_back,
           'shorts':total_shorts,
           "longs":total_longs
            }
       
       
       
        return output
    ii=0
    users=[]
        
    # gets unique number of  users
    unique_users=trades['user'].unique()
    
    # obtains info on each user
    
    for u in unique_users:
        users.append(get_stats_per_user(trades,u,ii));
        print('iteration %.f' % ii)
        ii+=1
    df=pd.DataFrame(users)
    if SAVEPATH is not None:
        df.to_pickle(SAVEPATH)
    return df



if __name__=='__main__':
    #sees if the trades pkl file exists, otherwise creates it
    from os.path import exists
    PATH_TRADES='trades.pkl'
    PATH_USERS='users.pkl'
    #tests if file exsirs
    if  exists(PATH_TRADES):
        trades=pd.read_pickle(PATH_TRADES)
    else:
        trades=load_drift_data()
        trades=format_drift_dataset(trades,SAVEPATH=PATH_TRADES)
    users=generate_user_dataframe(trades,SAVEPATH=PATH_USERS)
    
    
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


    
        
    