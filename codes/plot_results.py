#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Apr 25 11:46:28 2022

@author: juan
"""

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from statsmodels.graphics.tsaplots import plot_acf

plt.style.use('bmh')

trades=pd.read_csv('trades.csv')
users=pd.read_pickle('df_users.pkl')
#%%
plot_acf(trades['time_diff'][], lags=3000)
plt.show()