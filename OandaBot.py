import tkinter 
from src.ui.home import Home

class OandaBot(tkinter.Tk):
    def __init__(self):
        tkinter.Tk.__init__(self)
     
        self.title(
            'OandaBot'
        )
        self.geometry('1530x800')
        self.controller=self
        self.home = Home(self.master,self.controller)
        self.home.grid(row=0, column=0, columnspan=2, sticky='nsew')
        self.mainloop()

if __name__ == '__main__':
    
    OandaBot()