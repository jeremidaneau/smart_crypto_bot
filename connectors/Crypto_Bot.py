import csv, config
from binance.client import Client
import logging
import json
import ccxt
import config
import schedule
import pandas as pd
import warnings
import os


pd.options.display.max_rows = 2500
warnings.filterwarnings('ignore')
from datetime import datetime
import time
SYMBOL = 'ETHUSDT'
TRADE_SYMBOL = SYMBOL
TIME = "1m"

order_array = []
sell_array = []
order_file_path = 'coins_bought.csv'
array_order = []
array_sell = []

from datetime import date

today = date.today()
logger = logging.getLogger()

#Initiate CCXT Exchange
exchange = ccxt.binance({
    #'rateLimit': 10000,
    #'verbose': True,
    "apiKey": config.API_KEY,
    "secret": config.API_SECRET
})



STOP_LOSS = 1
TAKE_PROFIT = 2






class Crypto_Bot:
  def __init__(self, public_key: str, secret_key: str, testnet: bool,):
    self.public_key = public_key
    self.secret_key = secret_key
    self.in_position = False

    self.client = Client(self.public_key, self.secret_key)

  def tr(self,data):
    data['previous_close'] = data['close'].shift(1)
    data['high-low'] = abs(data['high'] - data['low'])
    data['high-pc'] = abs(data['high'] - data['previous_close'])
    data['low-pc'] = abs(data['low'] - data['previous_close'])

    tr = data[['high-low', 'high-pc', 'low-pc']].max(axis=1)

    return tr

  def atr(self,data, period):
    data['tr'] = self.tr(data)
    atr = data['tr'].rolling(period).mean()

    return atr

  def supertrend(self,df, period=7, atr_multiplier=3):
    hl2 = (df['high'] + df['low']) / 2
    df['atr'] = self.atr(df, period)
    df['upperband'] = hl2 + (atr_multiplier * df['atr'])
    df['lowerband'] = hl2 - (atr_multiplier * df['atr'])
    df['in_uptrend'] = True

    for current in range(1, len(df.index)):
      previous = current - 1

      if df['close'][current] > df['upperband'][previous]:
        df['in_uptrend'][current] = True
      elif df['close'][current] < df['lowerband'][previous]:
        df['in_uptrend'][current] = False
      else:
        df['in_uptrend'][current] = df['in_uptrend'][previous]

        if df['in_uptrend'][current] and df['lowerband'][current] < df['lowerband'][previous]:
          df['lowerband'][current] = df['lowerband'][previous]

        if not df['in_uptrend'][current] and df['upperband'][current] > df['upperband'][previous]:
          df['upperband'][current] = df['upperband'][previous]

    return df



  def check_buy_sell_signals(self,df):


    global montant
    print(df.tail(7))
    last_row_index = len(df.index) - 1
    previous_row_index = last_row_index - 1
    print("self.in_position")
    print(self.in_position)
    if not df['in_uptrend'][previous_row_index] and df['in_uptrend'][last_row_index]:
      print("changed to uptrend, buy")
      if not self.in_position:

        # maxBuy = buyAmount(PAIR_WITH, SYMBOL)

        # try:

        sell_array.clear()

        try:

          # BUY order
          order = exchange.create_market_buy_order(SYMBOL, 3500)
          print(order)

          order_array.append(order)

          self.update_porfolio()

          self.in_position = True

          logger.info("Buy order order: %s", order)
        except Exception as e:  # Takes into account any possible error, most likely network errors
          logger.error("error sell order%s",e)
          return None



      else:
        print("already in position, nothing to do")

    print("len(order_array")
    print(len(order_array))
    if self.in_position:

      take_profit = float(order_array[0]['price']) + (float(order_array[0]['price']) * TAKE_PROFIT) / 100
      stop_loose = float(order_array[0]['price']) - (float(order_array[0]['price']) * STOP_LOSS) / 100
      print("Trigger IN")
      print(take_profit)
      print('stop loose')
      print(stop_loose)



      if df['in_uptrend'][previous_row_index] and not df['in_uptrend'][last_row_index] or df['close'][
        last_row_index] >= take_profit or df['close'][last_row_index] <= stop_loose:
        # maxSell = sellAmount('BTC')
        # sell(maxSell, 'BTCUSDT')
        sell_amount = 0.995 * 3500
        try:
          # SELL order
          print("changed to downtrend, sell")
          order = exchange.create_market_sell_order(SYMBOL, sell_amount)

        # ord = json.dumps(order)
        # trade_order.writerow(ord)
          print(order)
          order_array.clear()
          sell_array.append(order)
          self.update_sell_porfolio()
          self.in_position = False
          logger.info("Sell order %s", order)
        except Exception as e:  # Takes into account any possible error, most likely network errors
          logger.error("error sell order %s",e)
          return None



  def update_porfolio(self,):

    if (len(order_array) > 0):

      for i in range(len(order_array)):
        print(i)
        print('trades')
        print(order_array[i]['trades'][0]['info'])
        print(order_array[i]['timestamp'])

        print('order_array price bought', order_array[0]['price'])
        print('order_array price bought', order_array[0]['symbol'])

        coins_order = {
          'symbol': order_array[i]['symbol'],
          'qty': order_array[i]['trades'][0]['info']['qty'],
          'tradeId': order_array[i]['trades'][0]['info']['tradeId'],
          'commission': order_array[i]['trades'][0]['info']['commission'],
          'timestamp': order_array[i]['timestamp'],
          'side': order_array[i]['side'],
          'bought_at': order_array[i]['price'],
          'trigger_out': order_array[i]['price'] + (order_array[i]['price'] * 0.01),
          'stop_loose': order_array[i]['price'] - (order_array[i]['price'] - 0.005),

          # 'volume': volume[coin]
        }

        array_order.append(coins_order)

    # print(coins_order)

    df_order = pd.DataFrame.from_dict(array_order)
    print(df_order)

    df_order = pd.DataFrame.from_dict(array_order)
    df_order['timestamp'] = pd.to_datetime(df_order['timestamp'], unit='ms')
    df_columns = ['symbol', 'qty', 'tradeId', 'commission', 'timestamp', 'bought_at', 'side']
    print("Df order")

    print(df_order)
    df_order.to_csv(TRADE_SYMBOL + str(today) + 'order_csv.csv')
    # df_order.to_csv(TRADE_SYMBOL + str(data_d[i]['timestamp']) + 'order_csv.csv')

  def update_sell_porfolio(self):

      if (len(sell_array) > 0):

        for i in range(len(sell_array)):
          print(i)
          print('trades sell')
          print(sell_array[i]['trades'][0]['info'])
          print(sell_array[i]['timestamp'])

          print('order_array price bought', sell_array[0]['price'])
          print('order_array price bought', sell_array[0]['symbol'])

          coins_sell_order = {
            'symbol': sell_array[i]['symbol'],
            'qty': sell_array[i]['trades'][0]['info']['qty'],
            'tradeId': sell_array[i]['trades'][0]['info']['tradeId'],
            'commission': sell_array[i]['trades'][0]['info']['commission'],
            'timestamp': sell_array[i]['timestamp'],
            'side': sell_array[i]['side'],
            'sell_at': sell_array[i]['price'],

            # 'volume': volume[coin]
          }

          array_sell.append(coins_sell_order)

      # print(coins_order)

      df_order = pd.DataFrame.from_dict(array_sell)
      print(df_order)

      df_sell_order = pd.DataFrame.from_dict(array_sell)
      df_sell_order['timestamp'] = pd.to_datetime(df_order['timestamp'], unit='ms')
      df_columns = ['symbol', 'qty', 'tradeId', 'commission', 'timestamp', 'sell_at', 'side']
      print("Df order")

      print(df_sell_order)
      df_sell_order.to_csv(TRADE_SYMBOL + str(today) + 'order_csv.csv',header=df_columns)
      # df_order.to_csv(TRADE_SYMBOL + str(data_d[i]['timestamp']) + 'order_csv.csv')

  def run_bot(self):


    print(f"Fetching new bars for {datetime.now().isoformat()}")
    bars = exchange.fetch_ohlcv(SYMBOL, timeframe=TIME, limit=20000)

    print(bars)
    df = pd.DataFrame(bars, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
    # df = pd.DataFrame(bars[:-1], columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')


    supertrend_data = self.supertrend(df)

    supertrend_data.to_csv(SYMBOL + "_supertrend.csv")

    self.check_buy_sell_signals(supertrend_data)


    print('order_array ', order_array)
    print('sel_array', sell_array)
    if len(order_array) > 0:
      print('order_array price bought', order_array[0]['price'])
      print('order_array price bought', order_array[0]['symbol'])




