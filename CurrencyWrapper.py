import ccxt
import botutils

class Currency:

    def __init__(self, name, key, secret):
        self.Name = name
        self.id = name
        self.Key = key
        self.Secret = secret
        self.Exchanges = {}
        self.Precisions = {}
        self.Balance = 0
        self.Available = 0
        self.Balance = botutils.balance(name, key)
        self.Available = self.Balance

    def add_exchange(self, exchange, balancesheet):

        if id in exchange.currencies:
            self.Exchanges[exchange.id] = {'total':balancesheet[self.id]['total'],'available':balancesheet[self.id]['free']}
            self.Precisions[exchange.id] = exchange.currencies[id]['precision']
            self.Balance += balancesheet[self.id]['total']
            self.Available += balancesheet[self.id]['free']

    def update_exchange(self, exchange, balancesheet):

        if exchange.id in self.Exchanges:
            self.Balance -= self.Exchanges[exchange.id]['total']
            self.Available -= self.Exchanges[exchange.id]['available']
            self.Exchanges[exchange.id] = {'total': balancesheet[self.id]['total'],
                                       'available': balancesheet[self.id]['free']}
            self.Balance += balancesheet[self.id]['total']
            self.Available += balancesheet[self.id]['free']

    def check_balance(self):
        return {"id":self.id, "total":self.Balance, "available":self.Available, "used":self.Balance-self.Available}

    def __str__(self):
        return self.Name
