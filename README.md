THIS IS A README FILE FOR  THE REPORT

There are two main folders: 

* `./writeup`. The main file here is  `main.tex`, which copiles the writeup. (`xelatex -synctex=1 -interaction=nonstopmode "main".tex`)
* `./codes` which contains the codes used to recreate the figures in the report. Here main files are the following:
    
    
    
 * `load_data.py`: this is the python script sent by Zane
 * `get_trades.py`: this file takes  the dataaframe from Zane script and formats it + adds some columns
 * `generate_user_df.py`: This file creates a dataframe with all the users and some of their attriburtes
 * `time_series.py`: generates the time siers analysis part of the code
 *  `generate_plots.py`: generates all figures from the report
    
Juan Pablo Madrigal Cianci
