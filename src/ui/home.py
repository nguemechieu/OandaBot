import datetime
import os
import tkinter 
from src.classes.oanda_trading_bot import OandaTradingBot
class  Home(tkinter.Frame):
    def __init__(self, master=None,controller=None):
        tkinter.Frame.__init__(self, master)
        self.controller=controller
        self.base_url = 'https://api-fxtrade.oanda.com/v3'
       
        self.server_msg = {
           'status': 'ONLINE',
           'message': ''
        }
        self.trades_list=[]
        self.units = 1
        self.time =datetime.datetime.now().strftime('%H:%M:%S %d/%m/%Y')


        self.instrument = 'EUR_USD'
        api_token = os.getenv("OANDA_API_TOKEN")
        account_id = os.getenv("OANDA_ACCOUNT_ID")
        
        self.bot = OandaTradingBot(account_id= account_id, api_token= api_token,instrument=self.instrument)
        

        self.start_btn = tkinter.Button(master, text='Start', command=lambda:self.start_trading(),bg='green',fg='white',font = ('Arial', 10, 'bold'))
        self.start_btn.place(relx=0.5, rely=0.5)
        self.stop_btn = tkinter.Button(master, text='Stop', command=lambda:self.stop_trading(),bg='red',fg='white',font = ('Arial', 10, 'bold'))
        self.stop_btn.place(relx=0.4, rely=0.5)
        self.reset_btn = tkinter.Button(master, text='Reset', command=lambda:self.reset_trading(),bg='yellow',fg='white',font = ('Arial', 10, 'bold'))
        self.reset_btn.place(relx=0.6, rely=0.5)

        
        self.canvas= tkinter.Canvas(self.master, width=1200, height=400,background='black',border=9 )   
        self.canvas.place(x=100, y=10)
   


        self.updates()



    def start_trading(self):
        self.bot.start()
        self.start_btn.config(state=tkinter.DISABLED,bg='gray')
        self.stop_btn.config(state=tkinter.NORMAL,bg='green')
    def stop_trading(self):
        self.bot.stop()
        self.stop_btn.config(state=tkinter.DISABLED,bg='gray')
        self.start_btn.config(state=tkinter.NORMAL,bg='green')

    def reset_trading(self):
        self.bot.reset()
    def updates(self):
        self.canvas.delete('all')
        self.canvas.create_text(300, 100, text='ID :'+self.bot.account_id.__str__(), font=('Arial', 10, 'bold'), fill='lightgreen')
        self.canvas.create_text(300, 150, text='TIME:'+self.time.__str__(), font=('Arial', 10, 'bold'), fill='lightgreen')
        self.canvas.create_text(300, 200, text='STATUS:'+self.bot.server_msg['status'].__str__(), font=('Arial', 10, 'bold'), fill='lightgreen')
        self.canvas.create_text(300, 250, text='MESSAGE:'+self.bot.server_msg['message'].__str__(), font=('Arial', 10, 'bold'), fill='lightgreen')
        self.canvas.create_text(300, 270, text=self.units.__str__())
        self.canvas.create_text(300, 300, text=self.bot.trades_list.__str__(), font=('Arial', 10, 'bold'), fill='lightgreen')
        self.canvas.create_text(300, 330, text=self.bot.symbol.__str__()+':'+self.bot.last_price.__str__(), font=('Arial', 10), fill='lightgreen')        

    