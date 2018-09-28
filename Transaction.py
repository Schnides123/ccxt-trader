import ccxt
import main
import botutils
import botconfig
class Transaction:

    def __init__(self):

        self.Data = {}
        self.Started = False
        self.Finished = False
        self.Next = None
        self.SummaryInfo = {}

    def push_tx(self):
        pass

    def cancel_tx(self):
        pass

    def check_status(self):
        pass

    def add_next(self, nxt):
        self.Next = nxt




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


class BuyTX(Transaction):

    def __init__(self, exchange, symbol, amount):

        super()
        self.Exchange = exchange
        self.Symbol = symbol
        self.Amount = amount
        self.SummaryInfo['cfrom'] = botutils.quote(symbol)
        self.SummaryInfo['cto'] = botutils.base(symbol)
        self.SummaryInfo['efrom'] = self.Exchange
        self.SummaryInfo['eto'] = self.Exchange
        self.SummaryInfo['amount'] = self.Amount
        self.OrderID = None
        self.Info = None
        self.Order = None

    def push_tx(self):

        #TODO:
        #create trade
        #get trade info and store to data
        #set Finished to flag from transaction data
        ex = self.Exchange.Ex
        if ex.fetch_balance()[self.SummaryInfo['cfrom']]['free'] < self.Amount:
            raise Exception('error: not enough funds')
        results = ex.create_limit_buy_order(self.Symbol, self.Amount, self.Exchange.estimate_sell_price_at(self.Symbol, self.Amount))
        if 'id' in [*results]:
            self.OrderID = results['id']
            self.Info = results['info']
            self.Started = True
            self.Order = ex.fetch_order(self.OrderID)

    def cancel_tx(self):

        if self.Started:
            ex = self.Exchange.Ex
            try:
                ex.cancel_order(self.OrderID)
                self.Started = False
            except:
                if ex.fetch_order(self.OrderID)['status'] == 'closed':
                    self.Finished = True

    def check_status(self):

        if self.OrderID is not None:
            ex = self.Exchange.Ex
            self.Order = ex.fetch_ordere(self.OrderID)
            if self.Order['status'] == 'closed':
                self.Finished = True
            if self.Order['status'] == 'cancelled':
                self.Started = False


class SellTX(Transaction):

    def __init__(self, exchange, symbol, amount):

        super()
        self.Exchange = exchange
        self.Symbol = symbol
        self.Amount = amount
        self.SummaryInfo['cfrom'] = botutils.base(symbol)
        self.SummaryInfo['cto'] = botutils.quote(symbol)
        self.SummaryInfo['efrom'] = self.Exchange
        self.SummaryInfo['eto'] = self.Exchange
        self.SummaryInfo['amount'] = self.Amount

    def push_tx(self):

        #TODO:
        #create trade
        #get trade info and store to data
        #set Finished to flag from transaction data
        ex = self.Exchange.Ex
        if ex.fetch_balance()[self.SummaryInfo['cfrom']]['free'] < self.Amount:
            raise Exception('error: not enough funds')
        results = ex.create_limit_sell_order(self.Symbol, self.Amount,
                                            self.Exchange.estimate_sell_price_at(self.Symbol, self.Amount))
        if 'id' in [*results]:
            self.OrderID = results['id']
            self.Info = results['info']
            self.Started = True
            self.Order = ex.fetch_order(self.OrderID)


