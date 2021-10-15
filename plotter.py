#data taken from yahoo finance for all stocks and cryptos listed
import pandas as pd
import plotly.express as px
import numpy as np
import math as m

#file name
filename = 'data/MSFT.csv'

#read data from csv file
data = pd.read_csv(filename)

#data to choose from
choose = 'Adj Close'

highs = data[choose]

#adds percent relative value to dataframe
def relativalue(ts):
    ts = list(ts)
    N = len(ts)
    for i in range(1, N):
        denom = ts[i-1]
        if denom == 0:
            denom = 0.0001
        t = round(ts[i] / denom, 5)
        data.at[i, (choose+' Relative Value')] = t
    return ts

#calculate the hurst exponent of a time series, modified from https://github.com/RyanWangZf/Hurst-exponent-R-S-analysis-/blob/master/Hurst.py
def hurst(ts):
    ts = list(ts)
    N = len(ts)
    
    # maximum number of lags
    max_k = int(np.floor(N/2))

    # Calculate the array of the variances of the subsets
    R_S_dict = []

    #calculate the mean of the time series
    for k in range(10,max_k+1):
        
        # calculate the rolling mean and standard deviation
        R,S = 0,0
        
        # split ts into subsets
        subset_list = [ts[i:i+k] for i in range(0,N,k)]
        
        # if the length of subset is not k, then we need to drop the last element
        if np.mod(N,k)>0:
            subset_list.pop()
        
        # calc mean of every subset
        mean_list=[np.mean(x) for x in subset_list]
        
        for i in range(len(subset_list)):
            list_sum = pd.Series(subset_list[i]-mean_list[i]).cumsum()
            R += max(list_sum)-min(list_sum)
            S += np.std(subset_list[i])
        R_S_dict.append({"R":R/len(subset_list),"S":S/len(subset_list),"n":k})
    
    # log transform and variance
    log_R_S, log_n = [], []
    
    leng = (len(R_S_dict))
    # calculate the log of R and S, finds the Hurst exponent
    for i in range(leng):
        spacing = np.spacing(1)
        dictelement = R_S_dict[i]
        data.at[i, 'Log RS'], data.at[i, 'Log N'] = rs_log, n_log = np.log((dictelement["R"]+spacing) / (dictelement["S"]+spacing)), np.log(dictelement["n"])
        log_R_S.append(rs_log)
        log_n.append(n_log)        

    # fit a line to the log of R and S
    Hurst_exponent = np.polyfit(log_n,log_R_S,1)[0]
    return Hurst_exponent


h = relativalue(highs)
hurst_h = hurst(data['Adj Close Relative Value'])
#print the hurst exponent
print("Hurst: ", hurst_h)

#save to CSV
data.to_csv(filename, index=False)

#graph the data
fig = px.line(data, x = 'Log N', y = 'Log RS', title=filename+' '+choose+'\'s. Hurst Exponent: '+str(hurst_h), width=600, height=400)
#fig = px.line(data, x = 'Date', y = 'Adj Close', title=filename+' '+choose+'\'s. Hurst Exponent: '+str(hurst_h))

#plot the graph
fig.show()
