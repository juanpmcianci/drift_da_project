#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Here we load data based on Zane's script


@author: Zane Salem
"""

from datetime import datetime 
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
pd.options.plotting.backend = "plotly"

#Loads data according to Zane's code
def load_drift_data(field='funding-rates', market='SOL-PERP'):
    def load_csv(ff):
        print('reading '+ff)
        return pd.read_csv(ff)
    url = 'https://drift-historical-data.s3.eu-west-1.amazonaws.com/program/'
    pid = 'dammHkt7jmytvbS3nHTxQNEcP59aE57nxwV21YdqEDN'
    year_months = ['2022/1', '2022/2', '2022/3', '2022/4']        
    market_str = ''
    if 'user' not in field:
        market_str = '/market/'+market+'/'
    else:
        year_months = ['2022']
    
    z = pd.concat([load_csv(url+pid+market_str+field+'/'+year_month) for year_month in year_months])
    return z