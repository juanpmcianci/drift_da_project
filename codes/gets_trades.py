#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Apr 20 08:08:22 2022

Here we manipulate the trades script a bit and add some additional fields

@author: juan
"""

from datetime import datetime 
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from load_data import load_drift_data



def format_drift_dataset(trades,alpha=0,SAVEPATH=None):
    '''
    Here we format the drift trade dataset for our purposes

    Parameters
    ----------
    trades : Pandas dataframe
        dataframe containing the drift dataset info.
    alpha: float between 0-1
        This is the parameter to determine the arbitrages.  we say there's an arbitrage if:
        (i) Transaction direction is Long and Mark<(1 − α)Oracle . 
        (ii) Transaction direction is Short and Mark>(1 + α)Oracle.
    SAVEPATH: str where to save a .pkl with the data. PLSEASE INCLUDE EXTENSION

    Returns
    -------
    trades same dataset, but correctly formated (right units per quantity) and some other columns, namely:
        humanTime: Transaction time given in a human readable way
        totalShorts: cummulative amount of short positions
        totalLongs: cummulative amount of long positions
        time_diff: time difference between trades, with a minimum of 1ms
        arb: whether the transaction was an alpha_arbitrage

    '''
    #sorts by trade time stamp
    trades=trades.sort_values(by='serverTimestamp')
    
    #removes some entries that are not too important for this case
    trades=trades.drop(columns=['refereeDiscount','referrerReward','tokenDiscount','historyIndex','marketIndex'])
    
    # puts data into the right format
    trades['oraclePrice']=trades['oraclePrice']/1e10
    trades['markPriceAfter']=trades['markPriceAfter']/1e10
    trades['markPriceBefore']=trades['markPriceBefore']/1e10
    trades['baseAssetAmount']=trades['baseAssetAmount']/1e13
    trades['quoteAssetAmount']=trades['quoteAssetAmount']/1e6
    trades['fee']=trades['fee']/1e6
    trades['markPrice']=np.array(trades['quoteAssetAmount'])/np.array(trades['baseAssetAmount'])
    #makes it human readable
    trades['humanTime']=pd.to_datetime(trades['serverTimestamp'],unit='ms')
    # creates vector of time differences, arbs and total longs/shorts
    td=np.zeros(len(trades))
    arb=np.zeros(len(trades))
    total_longs=np.zeros(len(trades))
    total_shorts=np.zeros(len(trades))
    VOL_ARB=0
    UB=1+alpha
    LB=1-alpha
    
    print('formatting, this might take some time ...')
    
    for i in range(len(trades)):
        
        if i>0:
            # computes time difference
            aux=trades['humanTime'].iloc[i]-trades['humanTime'].iloc[i-1]
            td[i]=aux.total_seconds()+1e-4 #(for stability)

            
        #tests for arbitrage
        if (trades['markPriceBefore'].iloc[i]<LB*trades['oraclePrice'].iloc[i]) and trades['direction'].iloc[i]=='Long':
            arb[i]=1
            VOL_ARB+=trades['quoteAssetAmount'].iloc[i]
        if (trades['markPriceBefore'].iloc[i]>UB*trades['oraclePrice'].iloc[i]) and trades['direction'].iloc[i]=='Short':
            arb[i]=1
            VOL_ARB+=trades['quoteAssetAmount'].iloc[i]
        #computes total number of longs/shorts
        if trades['direction'].iloc[i]=='Long':
            if trades['liquidation'].iloc[i]==True:
                total_longs[i]=-1
            else:
                total_longs[i]=1
        if trades['direction'].iloc[i]=='Short':
            if trades['liquidation'].iloc[i]==True:
                total_shorts[i]=-1
            else:
                total_shorts[i]=1
    
    
    total_longs=np.cumsum(total_longs)
    total_shorts=np.cumsum(total_shorts)
    trades['totalShorts']=total_longs
    trades['totalLongs']=total_shorts
    trades['humanTime'].iloc[0]
    trades['time_diff']=td
    trades['arb']=arb
    
    if SAVEPATH is not None:
        trades.to_pickle(SAVEPATH)

    return trades





if __name__=='__main__':
    print('generating dataset')
    #Loads data according to Zane's code
    trades=load_drift_data(field='trades')
    print('formating dataset')
    trades =format_drift_dataset(trades,alpha=0,SAVEPATH='trades.pkl')
    
    
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
    
    #%%
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
    
    
    
    #%% Plots log density of transaction amount. This is done so that it is easier to visualise
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
    #%%
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





    