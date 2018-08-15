import ccxt
import main
class Transaction:

    def __init__(self):

        self.Data = {}
        self.Started = False
        self.Finished = False
        self.SummaryInfo = {}


    def push_tx(self):
        self.Started = True


class TransferTX(Transaction):

    def __init__(self, exchangefrom, exchangeto, currency, amount):

        super()
        self.Currency = currency
        self.From = exchangefrom
        self.To = exchangeto
        self.Amount = amount
        self.SummaryInfo['cfrom'] = self.Currency
        self.SummaryInfo['cto'] = self.Currency
        self.SummaryInfo['efrom'] = self.From
        self.SummaryInfo['eto'] = self.To
        self.SummaryInfo['amount'] = self.Amount

    def push_tx(self):

        super.push_tx()
        #TODO:
        # get deposit address from To
        # call From.withdraw to deposit address To
        # get transaction info from exchange from and store to data
        # set Finished to deposit flag for transfer


class TradeTX(Transaction):

    def __init__(self, exchange, symbol, amount):

        super()
        self.Exchange = exchange
        #self.Market = exchange.markets[symbol]
        self.From = main.Currencies[symbol.split('/')[0]]
        self.To = main.Currencies[symbol.split('/')[1]]
        self.Amount = amount
        self.SummaryInfo['cfrom'] = self.From
        self.SummaryInfo['cto'] = self.To
        self.SummaryInfo['efrom'] = self.Exchange
        self.SummaryInfo['eto'] = self.Exchange
        self.SummaryInfo['amount'] = self.Amount

    def __init__(self, exchange, currencyfrom, currencyto, amount):

        super()
        self.Exchange = exchange
        self.From = currencyfrom
        self.To = currencyto
        self.Market = exchange.markets[self.From.Name + "/" + self.To.Name]
        self.Amount = amount
        self.SummaryInfo['cfrom'] = self.From
        self.SummaryInfo['cto'] = self.To
        self.SummaryInfo['efrom'] = self.Exchange
        self.SummaryInfo['eto'] = self.Exchange
        self.SummaryInfo['amount'] = self.Amount

    def push_tx(self):

        super.push_tx()
        #TODO:
        #create trade
        #get trade info and store to data
        #set Finished to flag from transaction data

