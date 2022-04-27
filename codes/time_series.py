#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
This module deals with the TSA part of the report. it requires META's prophet package
!pip install prophet
@author: juan
"""

# Python
import pandas as pd
from prophet import Prophet
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from statsmodels.graphics.tsaplots import plot_acf


def generate_tsa(times,variable,skip=100,SAVENAME=None,TITLE=None):
    '''
    

    Parameters
    ----------
    trades : pandas series
        series containing times in human readable format
    variable : pandas series
       series we want to analise
    skip : int, optional
        how many samples do we thin the time series by. This is done if the time series is too large
    SAVENAME: str
        path to save the file. DO NOT INCLUDE EXTENSION

    Returns
    -------
    m: prophet object with the fit
    fig_fore: figure with the forecast
    fig_comp: figure with the components

    '''

    
    times=times.iloc[::skip]
    variable=variable.iloc[::skip]
    #formats data according to prophet
    dd={
        'ds':np.array(times),
        'y':np.array(variable)
        }
    df1=pd.DataFrame(dd)
        
    m = Prophet()
    #fits the model
    m.fit(df1)
    future = m.make_future_dataframe(periods=10)
    future.tail()
    forecast = m.predict(future)
    forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].tail()

    fig_fore = m.plot(forecast)
    plt.tight_layout()
    plt.title(TITLE)
    plt.xlabel('time')
    plt.tight_layout()
    #saves figures
    if SAVENAME is not None:
        name=SAVENAME+'_forecast.png'
        plt.savefig(name)
    
    fig_comp = m.plot_components(forecast)
    plt.tight_layout()
    if SAVENAME is not None:
        name=SAVENAME+'_component.png'
        plt.savefig(name)

    return m,fig_fore,fig_comp
