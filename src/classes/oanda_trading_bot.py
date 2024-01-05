import threading
import random
import numpy as np
import sqlite3

import requests
import json
import time
import datetime

import pandas as pd

class OandaTradingBot:
    def __init__(self, account_id=None, api_token=None, instrument=None, units=0, base_url='https://api-fxtrade.oanda.com'):
        self.account_id='001-001-2783446-006'
        self.api_token =  '00684c0eb96969cc95ff036d41565e46-4123f61bd010c68026256db38e150f8f'

        self.engine= sqlite3.connect('db.sql')
        self.instrument = instrument
        self.units = units
        self.base_url = 'https://api-fxtrade.oanda.com'

        self.headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.api_token}',
            'Accept': 'application/json',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X  10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/ 537.36'

        }
        
        self.server_msg={
            'status':'OFFLINE',
            'lastTradeID': 0,
            'lastTradePrice': 0,
            'lastTradeTime': 0,
            'lastTradeTimestamp': 0,
            'lastTradeVolume': 0,
            'trades': [],
            'order': {},
            'message': '',
            'info': ''

        }

        self.order_types = [
            'LIMIT',
            'MARKET',
            'STOP_LOSS',
            'STOP_LOSS_LIMIT',
            'TAKE_PROFIT',
            'TAKE_PROFIT_LIMIT'
        ]

        self.order_states = [
            'PENDING',
            'FILLED',
            'CANCELED',
            'REJECTED',
            'PENDING_CANCEL'
        ]

        self.order_fill_types = [
            'DEFAULT',
            'GTC',
            'IOC',
            'FOK'
        ]

        self.order_side = [
            'BUY',
            'SELL'
        ]
        self.trade_id =2345
        self.order_state = None
        self.order_type = None
        self.order_fill_type = None
        self.order_side = None
        self.price = 0
        self.time =  datetime.datetime.now().strftime('%H:%M:%S %d/%m/%Y ')
        self.timestamp = self.time
        self.volume = 0
        self.order_id = 0
        self.trade_id = random.randint(1000000,9999999)
        self.trade_price = 0
        self.trade_time = 0
        self.order_type_list =['LIMIT','MARKET','STOP_LOSS','STOP_LOSS_LIMIT','TAKE_PROFIT' ,'TAKE_PROFIT_LIMIT']

        self.order_state_list = [
            'PENDING',
            'FILLED',
            'CANCELED',
            'REJECTED',
            'PENDING_CANCEL'
        ]

        self.account_id = account_id
    
        self.api_token = api_token


        self.order_id=0
        self.orders_list=[]
        self.trades_list=[]
        self.last_price = 0


        self.actions = ['BUY', 'SELL','STOP_LOSS','STOP_LOSS_LIMIT','TAKE_PROFIT','TAKE_PROFIT_LIMIT']

        if self.account_id is None:
            self.server_msg['status']='OFFLINE'
            self.server_msg['message']='Error getting the list of accounts\n.Please check your credentials'
            return
        self.symbols = []
        
        #Get the list of symbols
      
        symbol0 =self.get_account_instruments(self.account_id)

        self.symbols = pd.DataFrame(symbol0)
        self.symbols.to_csv('symbols.csv', index=False)
        
        self.symbols = self.symbols.reset_index(drop=True)
        self.symbols = self.symbols['name'].values
        print(self.symbols)
        
       
      

        self.symbol = self.symbols[0]

    
        self.trade_strategy = None

        self.trade_strategy = {
            'buy': {
                'price': 1.1200,
                'volume': 1000,
                'time': 1640000000000,
                'timestamp': 1640000000000
            },
          'sell': {
                'price': 1.1200,
                'volume': 1000,
                'time': 1640000000000,
                'timestamp': 1640000000000
            }
        }




#         CandlestickGranularity	The granularity of a candlestick
# Value	Description
# S5	5 second candlesticks, minute alignment
# S10	10 second candlesticks, minute alignment
# S15	15 second candlesticks, minute alignment
# S30	30 second candlesticks, minute alignment
# M1	1 minute candlesticks, minute alignment
# M2	2 minute candlesticks, hour alignment
# M4	4 minute candlesticks, hour alignment
# M5	5 minute candlesticks, hour alignment
# M10	10 minute candlesticks, hour alignment
# M15	15 minute candlesticks, hour alignment
# M30	30 minute candlesticks, hour alignment
# H1	1 hour candlesticks, hour alignment
# H2	2 hour candlesticks, day alignment
# H3	3 hour candlesticks, day alignment
# H4	4 hour candlesticks, day alignment
# H6	6 hour candlesticks, day alignment
# H8	8 hour candlesticks, day alignment
# H12	12 hour candlesticks, day alignment
# D	1 day candlesticks, day alignment
# W	1 week candlesticks, aligned to start of week
# M	1 month candlesticks, aligned to first day of the month
        
        self.grannularities = ['S5','S10','S15','S30','M1','M2','M4','M5','M10','M15','M3','H1','H2','H3','H4','H6','H8','H12','D','W','M']
        self.current_grannularity = self.grannularities[8]

    

        self.start_time = datetime.datetime.now()
        self.stop_time = 0
        self.timeframe = 0
        self.interval = 0
    
        self.selected_strategy = 'buy'
        self.selected_timeframe = '1m'
        self.selected_interval = 60
        # CANDELS used to create a list of candels
        self.candels = []

    
        self.thread = threading.Thread(target=self.run,args=())
        self.thread.daemon = True
        self.thread.start()
        self.server_msg['status']='ONLINE'
        






    def create_order(self, order_type, price=None):
        data = {
            'order': {
                'units': self.units,
                'instrument': self.instrument,
                'type': order_type,
                'positionFill': 'DEFAULT',
                'timeInForce': 'GTC',
                'clientID': self.account_id,
                'tradeID': self.trade_id,
            }
        }

        if order_type == 'STOP_LOSS' and price:
            data['order']['price'] = str(price)
            self.last_price = price

        response = requests.post(
            f'{self.base_url}/v3/accounts/{self.account_id}/orders',
            headers=self.headers,
            data=json.dumps(data), timeout=5000
        )

        return response.json()

    def get_price(self):
        response = requests.get(
            f'{self.base_url}/v3/accounts/{self.account_id}/pricing?instruments={self.instrument}',
            headers=self.headers, timeout=5000
        )

        print(response.json())

        price = response.json()['prices'][0]['closeoutAsk']
        return float(price)

    def run(self):


        while True:

            # Get the current time
            current_time = datetime.datetime.now()
            self.time = current_time.strftime('%H:%M:%S')
            #Get the current date
            self.date = current_time.strftime('%Y-%m-%d')
            self.symbol = 'EUR_USD'
       
        
            # Get the candles
            response = requests.get(url="https://api-fxtrade.oanda.com/v3/instruments/"+self.symbol+"/candles?count=6&price=M&granularity=M5"
                ,
                headers=self.headers, timeout=5000
            )

            if response.status_code == 200:
             candles = response.json()['candles']
             print(candles)
             mid_pd = pd.DataFrame( columns=['time','o','h','l','c','v'])
             for kk in candles:
               
                 if kk =='complete':
                     mid_pd['complete'] = candles[kk]
                     print(mid_pd['complete'])
                 if kk == 'mid':
                    for mm in candles[kk]:
                        mid_pd[mm] = candles[kk][mm]
                        print(mid_pd[mm])
              
                   
                         

            
            #Save the candles into pandas dataframe
        
             mid_pd.to_csv('candles.csv', index=False)

            #Save the candles into sqlite database
             engine = sqlite3.connect('db.sql')
             mid_pd.to_sql('candles', con=engine, if_exists='replace', index=False)
            
            else:
                print(response.status_code)
                print(response.json())
                self.stop = True
                self.server_msg['status'] = 'OFFLINE'
                self.server_msg['message'] = f'Error getting candles for {self.symbol}'
        
            self.trades_list.append(self.trade_id)

         






            # Get the current price
            current_price = self.get_price()

            # Example strategy: Buy if the price is below a certain threshold
            if current_price < 1.1200:
                # Create a market order to buy
                response = self.create_order('STOP_LOSS', 1.1200)
                print('Buy Order:', response)

            time.sleep(60)  # Sleep for 60 seconds (adjust as needed)
            print(f'Current price: {current_price}')
    def stop(self):
        self.start_bot = False

        self.server_msg['status'] = 'OFFLINE'
        self.server_msg['message'] = 'Stopped trading '
        if self.thread.is_alive():
             self.thread.join()

        
    def start(self):
     
            self.server_msg['status'] = 'ONLINE'
            self.server_msg['lastTradeID'] = self.trade_id
            self.server_msg['lastTradePrice'] = self.trade_price
            self.server_msg['lastTradeTime'] = self.time
            self.server_msg['lastTradeTimestamp'] = self.timestamp
            self.server_msg['lastTradeVolume'] = self.volume
            self.server_msg['trades'] = self.trades_list
            self.server_msg['order'] = self.order_id
            self.server_msg['message'] = ''
            while self.stop == False:
             self.thread.start()
             self.server_msg['status'] = 'ONLINE'
            
             time.sleep(1)
         
     
    def reset(self):
        self.stop = False
        self.start = False
        self.server_msg['status'] = 'ONLINE'
        self.server_msg['message'] = f'Reset trading ...'
        return
    
    
# GET	/v3/accounts
# Get a list of all Accounts authorized for the provided token.
    def get_accounts(self):
        response = requests.get(
            f'{self.base_url}/v3/accounts',
            headers=self.headers, timeout=5000
        )
        if response.status_code == 200:
            return response.json()['accounts']
        else:
            print(response.status_code)
            print(response.json())
            self.server_msg['status'] = 'ACCOUNTS_ERROR'
            self.server_msg['message'] = f'Error getting accounts'
            return []


# GET	/v3/accounts/{accountID}
# Get the full details for a single Account that a client has access to. Full pending Order, open Trade and open Position representations are provided.

    def get_account(self, account_id):
        response = requests.get(
            f'{self.base_url}/v3/accounts/{account_id}',
            headers=self.headers, timeout=5000
        )
        if response.status_code == 200:
            return response.json()['account']
        else:
            print(response.status_code)
            print(response.json())
            self.server_msg['status'] = 'ACCOUNT_ERROR'
            self.server_msg['message'] = f'Error getting account'
            return []
# GET	/v3/accounts/{accountID}/summary
# Get a summary for a single Account that a client has access to.
    def get_account_summary(self, account_id):
        response = requests.get(
            f'{self.base_url}/v3/accounts/{account_id}/summary',
            headers=self.headers, timeout=5000
        )
        if response.status_code == 200:
            return response.json()['summary']
        else:
            print(response.status_code)
            print(response.json())
            self.server_msg['status'] = 'ACCOUNT_SUMMARY_ERROR'
            self.server_msg['message'] = f'Error getting account summary'
            return []

# GET	/v3/accounts/{accountID}/instruments
# Get the list of tradeable instruments for the given Account. The list of tradeable instruments is dependent on the regulatory division that the Account is located in, thus should be the same for all Accounts owned by a single user.
    def get_account_instruments(self, account_id):
        response = requests.get(
            f'{self.base_url}/v3/accounts/{account_id}/instruments',
            headers=self.headers, timeout=5000
        )
        if response.status_code == 200:
            return response.json()['instruments']
        else:
            print(response.status_code)
            print(response.content)
            self.server_msg['status'] = 'ACCOUNT_INSTRUMENTS_ERROR'
            self.server_msg['message'] = f'Error getting account instruments'+ f'for {account_id}'
            return []

# PATCH	/v3/accounts/{accountID}/configuration
# Set the client-configurable portions of an Account.
    def patch_account_configuration(self, account_id, configuration):
        response = requests.patch(
            f'{self.base_url}/v3/accounts/{account_id}/configuration',
            headers=self.headers, data=json.dumps(configuration), timeout=5000
        )
        if response.status_code == 200:
            return response.json()['configuration']
        else:
            print(response.status_code)
            print(response.json())
            self.server_msg['status'] = 'ACCOUNT_CONFIGURATION_ERROR'
            self.server_msg['message'] = f'Error getting account configuration'
            return []

# GET	/v3/accounts/{accountID}/changes
# Endpoint used to poll an Account for its current state and changes since a specified TransactionID.
    def get_account_changes(self, account_id, transaction_id):
        response = requests.get(
            f'{self.base_url}/v3/accounts/{account_id}/changes?transactionID={transaction_id}',
            headers=self.headers, timeout=5000
        )
        if response.status_code == 200:
            return response.json()['changes']
        else:
            print(response.status_code)
            print(response.json())
            self.server_msg['status'] = 'ACCOUNT_CHANGES_ERROR'
            self.server_msg['message'] = f'Error getting account changes'
            return []
    
