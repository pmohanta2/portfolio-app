#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd
import numpy as np
import yfinance as yf
import nsepy as ns
import datetime
import plotly.express as px
import streamlit as st

import warnings
warnings.filterwarnings('ignore')


# In[ ]:


st.markdown('<style>body{background-color: Blue;}</style>',unsafe_allow_html=True)
st.title("Portfolio")


# In[2]:


with st.form("my_form"):
    begin = st.date_input("start_date")
    end = st.date_input("end_date")
    n_day_measure_perf = st.number_input(label = 'number of days to measure performance' )
    top_n_stocks = int(st.number_input(label = 'number of stocks for performance measure'))
    int_invest = st.number_input(label = 'initial investment')
    
    if begin == end :
        st.warning('both dates are same!!')
    submitted = st.form_submit_button("Submit")


# In[ ]:





# In[ ]:


URL = 'https://archives.nseindia.com/content/indices/ind_nifty50list.csv'
df = pd.read_csv(URL, index_col = 'Company Name')
df['Yahoo_Symbol']='Hello World'
df.Yahoo_Symbol= df.Symbol + '.NS'
nifty_50_list = df['Yahoo_Symbol'].tolist()


# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:


def CAGR(data):
    df = data.copy()
    trading_days = 252
    n = len(df)/ trading_days
    cagr = (np.power((df['Equity Curve'][-1]/df['Equity Curve'][0]),1/n)-1) * 100
    return cagr

def daily_return(data):
    df = data.copy()
    lst = []
    for i in range(1,len(data)):
        rtrn = df['Equity Curve'][i] - df['Equity Curve'][i-1]
        lst.append(rtrn)
    return lst

def volatility(data):
    dr = np.array(daily_return(data))
    volat = np.power(np.std(dr),1/252) * 100
    return volat

def sharpe_ratio(data):
    dr = np.array(daily_return(data))
    s_ratio = np.power((np.mean(dr)/np.std(dr)),1/252)
    return s_ratio


# In[ ]:





# In[ ]:


if submitted:
    
##################################################################################
    df = yf.download(nifty_50_list,start=begin,end=end)
    eq_allo = int_invest/50
    
    qty =  pd.DataFrame().reindex_like(df['Open'])
    dv =  pd.DataFrame().reindex_like(df['Open'])
    
    for i in range(len(df.Open.iloc[1,:])):
        qty.iloc[:,i] = eq_allo // df.Open.iloc[0,i]
    
    for i in range(len(df.Open.iloc[:,1])):
        for j in range(len(df.Open.iloc[1,:])):
            dv.iloc[i,j] = qty.iloc[i,j] * df.Close.iloc[i,j]
        
    dd = df[['Open','Close']]
    dd = pd.concat([dd, pd.concat({'Qty': qty}, axis=1)], axis=1)
    dd = pd.concat([dd, pd.concat({'Daily Value': dv}, axis=1)], axis=1)
    
    lst = []
    for i in range(len(dd['Daily Value'].iloc[:,1])):
        sum = 0
        for j in range(len(dd['Daily Value'].iloc[1,:])):
            sum += dd['Daily Value'].iloc[i,j]
        lst.append(sum)
    dd['Equity Curve'] = lst

    
    
####################################################################################
    topn_allo = int_invest/top_n_stocks
    #100 days past data
    past_end = begin - pd.DateOffset(1)
    past_st = begin - pd.DateOffset(n_day_measure_perf)
    past_st = past_st.strftime('%Y-%m-%d')
    past_ed = past_end.strftime('%Y-%m-%d')
    past_df = yf.download(nifty_50_list,start = past_st,end = past_ed)

    lst = []
    for stock in nifty_50_list:
        performance  = (past_df['Close',stock][-1]/past_df['Close',stock][0])-1
        lst.append([stock,performance])
    datafr = pd.DataFrame(lst)
    topn = datafr.nlargest(top_n_stocks,[1])[0].values.tolist()
    
    #getting data of top n performing stocks
    topn_df = yf.download(topn,start=begin,end=end)
    topn_qty =  pd.DataFrame().reindex_like(topn_df['Open'])
    topn_dv =  pd.DataFrame().reindex_like(topn_df['Open'])
    
    #for quantity
    for i in range(len(topn_df.Open.iloc[1,:])):
        topn_qty.iloc[:,i] = topn_allo // topn_df.Open.iloc[0,i]
    # For Daily Value    
    for i in range(len(topn_df.Open.iloc[:,1])):
        for j in range(len(topn_df.Open.iloc[1,:])):
            topn_dv.iloc[i,j] = topn_qty.iloc[i,j] * topn_df.Close.iloc[i,j]
    
    topn_df = topn_df[['Open','Close']]
    topn_df = pd.concat([topn_df, pd.concat({'Qty': topn_qty}, axis=1)], axis=1)
    topn_df = pd.concat([topn_df, pd.concat({'Daily Value': topn_dv}, axis=1)], axis=1)
    
    lst = []
    for i in range(len(topn_df['Daily Value'].iloc[:,1])):
        sum = 0
        for j in range(len(topn_df['Daily Value'].iloc[1,:])):
            sum += topn_df['Daily Value'].iloc[i,j]
        lst.append(sum)
    topn_df['Equity Curve'] = lst
##########################################################################################    
    # Getting niftyindex data
    nifty = ns.get_history('NIFTY',start = begin, end = end, index = True)
    ni= nifty[['Open','Close']]
    ni['Qty'] = int_invest // ni['Open'][0]
    ni['Daily Value'] = ni['Close'] * ni['Qty']
    ni['Equity Curve'] = ni['Daily Value']
    
##########################################################################################   
    fig = px.line(width=800, height=600, title='Equity Curve', template='plotly_white')
    fig.add_scatter( x=ni.index, y=ni['Equity Curve'],mode ='lines', name = "EC_nifty")
    fig.add_scatter( x=topn_df.index, y=topn_df['Equity Curve'],mode ='lines', name = "EC_top_n")
    fig.add_scatter( x=dd.index, y=dd['Equity Curve'],mode ='lines', name = "EC_all")
    st.plotly_chart(fig)
##########################################################################################    
    st.write('Performance metrics:')
    table = pd.DataFrame(index = ['Equal allo buy hold','Nifty','Performance_stat'],columns=['CAGR %','VOLATILITY %','Sharpe'])
    table['CAGR %'] =[CAGR(dd),CAGR(ni),CAGR(topn_df)]
    table['VOLATILITY %'] =[volatility(dd),volatility(ni),volatility(topn_df)]
    table['Sharpe'] =[sharpe_ratio(dd),sharpe_ratio(ni),sharpe_ratio(topn_df)]
    st.table(table)
    
    st.write('Top Stocks Selected:')
    st.write(np.array(top).tolist())
    

