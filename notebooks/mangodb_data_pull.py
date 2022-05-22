import pymongo
from pymongo import MongoClient
import pandas as pd
import json
import numpy as np


#GAL ALPINE ANC

symbol = "ANC"
pair_sym = symbol+"USDT"



myclient = pymongo.MongoClient("mongodb+srv://dbJeremi:55!8!961lBe58bly9FJBLwE9@BinanceStream.4ic4a.mongodb.net/test")
db = myclient["binance"]


col_trade = db["trade"]
#col_kline_1m = db["kline_1m"]
col_aggtrade = db["aggtrade"]
col_book_ticker = db["bookticker"]


print("Number in the collection Bookticker: "+str(db["bookticker"].count_documents({"symbol":pair_sym})))
print("Number in the collection Trade: "+str(db["trade"].count_documents({"symbol":pair_sym})))
print("Number in the collection aggtrade: "+str(db["aggtrade"].count_documents({"symbol":pair_sym})))


col_trade_ = col_trade.find({"symbol":pair_sym}).limit(20000).sort("time", 1)
col_aggtrade_ = col_aggtrade.find({"symbol":pair_sym}).limit(20000).sort("time", -1)
col_bookticker_ = col_book_ticker.find({"symbol":pair_sym}).limit(20000).sort("time", -1)

#new_book = col_book_ticker.find({"symbol":"GALUSDT"}).limit(5000).sort("time", -1)


data_trade = pd.DataFrame(list(col_trade_))
data_aggtrade = pd.DataFrame(list(col_aggtrade_))
data_bookticker = pd.DataFrame(list(col_bookticker_))
#data_new_book  = pd.DataFrame(list(new_book))
#for x in col_:
    #print(x)

data_bookticker = data_bookticker.drop(["order_book_updateId"], axis=1)

#Transformations to add minute aggrigation to the data

df_minute_aggtrade = data_aggtrade.copy()
df_minute_aggtrade = data_aggtrade.sort_values(by='time')
df_minute_aggtrade['unix'] = pd.to_datetime(df_minute_aggtrade['time']).map(pd.Timestamp.timestamp)
pos = df_minute_aggtrade.columns.get_loc('unix')
df_minute_aggtrade['time_id'] = (df_minute_aggtrade.iloc[1:,pos]-df_minute_aggtrade.iat[0,pos])//60
df_minute_aggtrade['time_id'] = df_minute_aggtrade['time_id'].fillna(0)

df_minute_data_bookticker = data_bookticker.copy()
df_minute_data_bookticker = df_minute_data_bookticker.sort_values(by='time')
df_minute_data_bookticker['unix'] = pd.to_datetime(df_minute_data_bookticker['time']).map(pd.Timestamp.timestamp)
pos = df_minute_data_bookticker.columns.get_loc('unix')
df_minute_data_bookticker['time_id'] = (df_minute_data_bookticker.iloc[1:,pos]-df_minute_data_bookticker.iat[0,pos])//60
df_minute_data_bookticker['time_id'] = df_minute_data_bookticker['time_id'].fillna(0)

df_minute_data_trade = data_trade.copy()
df_minute_data_trade = df_minute_data_trade.sort_values(by='time')
df_minute_data_trade['unix'] = pd.to_datetime(df_minute_data_trade['time']).map(pd.Timestamp.timestamp)
pos = df_minute_data_trade.columns.get_loc('unix')
df_minute_data_trade['time_id'] = (df_minute_data_trade.iloc[1:,pos]-df_minute_data_trade.iat[0,pos])//60
df_minute_data_trade['time_id'] = df_minute_data_trade['time_id'].fillna(0)