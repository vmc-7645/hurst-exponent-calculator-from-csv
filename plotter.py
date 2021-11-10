#data taken from yahoo finance for all stocks and cryptos listed
import pandas as pd
import plotly.express as px
import numpy as np
import math as m

#file name
filename = 'data/MSFTyearly.csv' #The file name of the data to be used in our analysis

#read data from csv file
data = pd.read_csv(filename) #Reading the data from the csv file referenced in the filename variable

#data to choose from
choose = 'Adj Close' #Selecting the data to be used in the analysis from our loaded file

#the highs variable
highs = data[choose] #Selects the data to be used in the analysis

#adds percent relative value to dataframe
def relativalue(ts):
    ts = list(ts) #convert to list
    N = len(ts) #length of time series
    for i in range(1, N):
        denom = ts[i-1] #denominator
        if denom == 0: #if denominator is 0, set to a small value (0.0001) so as to avoid division by 0
            denom = 0.0001 # setting to a small value
        t = round(ts[i] / denom, 5)# calculate the relative value
        data.at[i, (choose+' Relative Value')] = t#add to dataframe
    return ts #return the time series

#calculate the hurst exponent of a time series, modified from https://github.com/RyanWangZf/Hurst-exponent-R-S-analysis-/blob/master/Hurst.py
def hurst(ts):
    #time series
    ts = list(ts) #convert to list

    #number of elements in time series
    N = len(ts) #length of time series
    
    # maximum number of lags
    max_k = int(np.floor(N/2)) #maximum number of lags

    # Calculate the array of the variances of the subsets
    R_S_dict = [] #empty list to store the R_S values

    #calculate the mean of the time series
    for k in range(10,max_k+1): #for each lag
        
        # calculate the range and standard deviation
        R,S = 0,0 #initialize range and standard deviation
        
        # split ts into subsets
        subset_list = [ts[i:i+k] for i in range(0,N,k)]
        
        # if the length of subset is not k, then we need to drop the last element
        if np.mod(N,k)>0:
            subset_list.pop() #remove last element
        
        # calc mean of every subset
        mean_list=[np.mean(x) for x in subset_list] #calculate the mean of each subset
        
        # calculate the range and standard deviation
        for i in range(len(subset_list)): #for each subset
            list_sum = pd.Series(subset_list[i]-mean_list[i]).cumsum() #calculate the cumulative sum of the subset
            R += max(list_sum)-min(list_sum) #calculate the range
            S += np.std(subset_list[i]) #calculate the standard deviation
        R_S_dict.append({"R":R/len(subset_list),"S":S/len(subset_list),"n":k}) #append to list
    
    # log transform and variance
    log_R_S, log_n = [], [] #empty lists to store the log transformed values
    
    leng = (len(R_S_dict))
    # calculate the log of R and S, finds the Hurst exponent
    for i in range(leng): #for each lag
        spacing = np.spacing(1) #calculate the spacing
        dictelement = R_S_dict[i] #get the dictionary element
        data.at[i, 'Log RS'], data.at[i, 'Log N'] = rs_log, n_log = np.log((dictelement["R"]+spacing) / (dictelement["S"]+spacing)), np.log(dictelement["n"]) #add to dataframe
        log_R_S.append(rs_log) #append to list
        log_n.append(n_log) #append to list

    # fit a line to the log of R and S
    Hurst_exponent = np.polyfit(log_n,log_R_S,1)[0] #Hurst = to the log of R and S
    return Hurst_exponent #return the Hurst exponent value of the time series


h = relativalue(highs)
hurst_h = hurst(data['Adj Close Relative Value'])
# #print the hurst exponent
print("Hurst: ", hurst_h) #print the hurst exponent

#save to CSV
data.to_csv(filename, index=False) #save the dataframe to a csv file

#graph the data
fig = px.line(data, x = 'Log N', y = 'Log RS', title=filename+' '+choose+'\'s. Hurst Exponent: '+str(hurst_h), width=600, height=400)
#fig = px.line(data, x = 'Date', y = 'Adj Close Relative Value', title=filename+' '+choose+'\'', width=600, height=400)

#plot the graph
fig.show()
