import warnings
from datetime import datetime
import pandas as pd
import MetaTrader5 as mt5
import numpy as np
import csv  
warnings.filterwarnings("ignore")
import os
import time
import csv


mt5.initialize("C:\\Program Files\\Genial Investimentos MetaTrader 5\\terminal64.exe")


class MT5:

   def get_data(symbol, n, timeframe=mt5.TIMEFRAME_M10):
        """ Function to import the data of the chosen symbol"""

        # Initialize the connection if there is not
        mt5.initialize("C:\\Program Files\\Genial Investimentos MetaTrader 5\\terminal64.exe")
                

        # Current date extract
        utc_from = datetime.now()

        # Import the data into a tuple
        rates = mt5.copy_rates_from(symbol, timeframe, utc_from, n)

        # Tuple to dataframe
        rates_frame = pd.DataFrame(rates)

        # Convert time in seconds into the datetime format
        rates_frame['time'] = pd.to_datetime(rates_frame['time'], unit='s')

        # Convert the column "time" in the right format
        rates_frame['time'] = pd.to_datetime(rates_frame['time'], format='%Y-%m-%d')

        # Set column time as the index of the dataframe
        rates_frame = rates_frame.set_index('time')
        return rates_frame

   def orders(symbol, lot, buy=True, id_position=None):
       """ Send the orders """
       
       # Initialize the connection if there is not
       if mt5.initialize() == False:
           mt5.initialize()

       # Get filling symbol 
       filling_symbol = mt5.symbol_info(symbol).filling_symbol - 1

       # Take ask price
       ask_price = mt5.symbol_info_tick(symbol).ask

       # Take bid price
       bid_price = mt5.symbol_info_tick(symbol).bid

       # Take the point of the asset
       point = mt5.symbol_info(symbol).point

       deviation = 20  # mt5.getSlippage(symbol)
       # **************************** Open a trade *****************************
       if id_position == None:

           # Buy order Parameters
           if buy:
               type_trade = mt5.ORDER_TYPE_BUY
               sl = ask_price - 2000 * point
               tp = ask_price + 2000 * point
               price = ask_price

           # Sell order Parameters
           else:
               type_trade = mt5.ORDER_TYPE_SELL
               sl = bid_price + 2000 * point
               tp = bid_price - 2000 * point
               price = bid_price

           # Open the trade
           request = {
               "action": mt5.TRADE_ACTION_DEAL,
               "symbol": symbol,
               "volume": lot,
               "type": type_trade,
               "price": price,
               "deviation": deviation,
               "sl": sl,
               "tp": tp,
               "magic": 234000,
               "comment": "python ML",
               "type_time": mt5.ORDER_TIME_GTC,
               "type_filling": filling_symbol,
           }
           # send a trading request
           result = mt5.order_send(request)
           result_comment = result.comment

       # **************************** Close a trade *****************************
       else:
           # Buy order Parameters
           if buy:
               type_trade = mt5.ORDER_TYPE_SELL
               price = bid_price

           # Sell order Parameters
           else:
               type_trade = mt5.ORDER_TYPE_BUY
               price = ask_price

           # Close the trade
           request = {
               "action": mt5.TRADE_ACTION_DEAL,
               "symbol":  symbol,
               "volume": lot,
               "type": type_trade,
               "position": id_position,
               "price": price,
               "deviation": deviation,
               "magic": 234000,
               "comment": "python ML",
               "type_time": mt5.ORDER_TIME_GTC,
               "type_filling": filling_symbol,
           }

           # send a trading request
           result = mt5.order_send(request)
           result_comment = result.comment
       return result.comment

   def resume():
      """ Return the current positions. Position=0 --> Buy """
      # Initialize the connection if there is not
      mt5.initialize()

      # Define the name of the columns that we will create
      colonnes = ["ticket", "position", "symbol", "volume"]

      # Go take the current open trades
      current = mt5.positions_get()

      # Create a empty dataframe
      summary = pd.DataFrame()

      # Loop to add each row in dataframe
      # (Can be ameliorate using of list of list)
      for element in current:
           element_pandas = pd.DataFrame([element.ticket,
                                          element.type,
                                          element.symbol,
                                          element.volume],
                                         index=colonnes).transpose()
           summary = pd.concat((summary, element_pandas), axis=0)

      return summary


   def run(symbol, long, short, lot):

        # Initialize the connection if there is not
        if mt5.initialize() == False:
            mt5.initialize()

        # Choose your  symbol
        print("------------------------------------------------------------------")
        print("Date: ", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        print("SYMBOL:", symbol)

        # Initialize the device
        current_open_positions = MT5.resume()
        # Buy or sell
        print(f"BUY: {long} \t  SHORT: {short}")

        """ Close trade eventually """
       

        """ Buy or short """
        if long==True:
            os.remove(f"C:\\Users\\Adminx\\AppData\\Roaming\\MetaQuotes\\Terminal\\Common\\Files\\Sinal_{lot}.csv")
            res = ['0']
            with open(f"C:\\Users\\Adminx\\AppData\\Roaming\\MetaQuotes\\Terminal\\Common\\Files\\Sinal_{lot}.csv", 'w', encoding='UTF8') as f:
                writer = csv.writer(f)
                writer.writerow(res)
                time.sleep(2)
            
            res = ['1']
            with open(f"C:\\Users\\Adminx\\AppData\\Roaming\\MetaQuotes\\Terminal\\Common\\Files\\Sinal_{lot}.csv", 'w', encoding='UTF8') as f:
                writer = csv.writer(f)
                writer.writerow(res)  
            
            print(f"OPEN LONG TRADE: {res}")

        if short==True:
            os.remove(f"C:\\Users\\Adminx\\AppData\\Roaming\\MetaQuotes\\Terminal\\Common\\Files\\Sinal_{lot}.csv")
            res = ['0']
            with open(f"C:\\Users\\Adminx\\AppData\\Roaming\\MetaQuotes\\Terminal\\Common\\Files\\Sinal_{lot}.csv", 'w', encoding='UTF8') as f:
                writer = csv.writer(f)
                writer.writerow(res)
                time.sleep(2)
            
            res = ['-1']
            with open(f"C:\\Users\\Adminx\\AppData\\Roaming\\MetaQuotes\\Terminal\\Common\\Files\\Sinal_{lot}.csv", 'w', encoding='UTF8') as f:
                writer = csv.writer(f)
                writer.writerow(res) 
            print(f"OPEN SHORT TRADE: {res}")

        print("------------------------------------------------------------------")

   def close_all_night():
        result = MT5.resume()
        for i in range(len(result)):
            before =  mt5.account_info().balance
            row = result.iloc[0+i:1+i,:]
            if row["position"][0]==0:
                res = MT5.orders(row["symbol"][0], row["volume"][0], buy=True, id_position=row["ticket"][0])

            else:
                res = MT5.orders(row["symbol"][0], row["volume"][0], buy=False, id_position=row["ticket"][0])