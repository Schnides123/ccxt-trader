class MarketRecord:

    def __init__(self, symbol):
        self.Symbol = symbol
        self.Base = symbol.split('/')[0]
        self.Quote = symbol.split('/')[1]
        self.Orders = []
        self.BestBid = -1
        self.BestAsk = -1

    def add_order(self, order, exchange):
        self.Orders.append(order)
        if order['bids'][0][0] > self.BestBid:
            self.BestBidOrder = order
            self.BestBid = order['bids'][0][0]
            self.BestBidEx = exchange
        if order['asks'][0][0] < self.BestAsk or self.BestAsk == -1:
            self.BestAskOrder = order
            self.BestAsk = order['asks'][0][0]
            self.BestAskEx = exchange

    def bid_price(self):
        return self.BestBid

    def ask_price(self):
        return self.BestAsk

    def bid(self):
        if len(self.Orders) > 0:
            return self.BestBidOrder

    def ask(self):
        if len(self.Orders) > 0:
            return self.BestAskOrder

    def bid_exchange(self):
        return self.BestBidEx

    def ask_exchange(self):
        return self.BestAskEx


class PriceEntry:

    def __init__(self, exchange, book, symbol, isbid):
        self.Price = book['bids'][0][0] if isbid else book['asks'][0][0]
        self.Exchange = exchange
        self.OrderBook = book
        self.Symbol = symbol
        self.Base = symbol.split("/")[0]
        self.Quote = symbol.split("/")[1]
        self.Bid = isbid
        self.Fees = exchange.fees['trading']['taker']

    def estimate_fee_percent(self, price, volume):
        feepercent = self.estimate_fees(price, volume)
        feepercent /= (price*volume)
        return feepercent

    def estimate_fees(self, price, volume):
        fee = self.Fees * price * volume
        depositFees = self.Exchange.fees['funding']['deposit']
        if self.Base in [*depositFees]:
            fee += depositFees[self.Base] * price if not self.Bid else 1.0
        withdrawFees = self.Exchange.fees['funding']['withdraw']
        if self.quote in [*withdrawFees]:
            fee += withdrawFees[self.Quote] * price if self.Bid else 1.0
        return fee

    def get_price(self):
        return self.Price * (1.0 - self.Fees if self.Bid else 1.0 + self.Fees)


class ArbitrageList:

    def __init__(self, symbol):
        self.BidList = []
        self.AskList = []
        self.Symbol = symbol
        self.BidPrice = 0
        self.AskPrice = 0

    def add_order(self, book, exchange, symbol):
        entry = PriceEntry(exchange, book, symbol, True)
        for i in range(0, len(self.BidList)):
            if self.BidList[i].get_price() < entry.get_price():
                self.BidList.insert(i, entry)
                if i == 0:
                    self.BidPrice = entry.get_price()
        askentry = PriceEntry(exchange, book, symbol, False)
        for i in range(0, len(self.AskList)):
            if self.AskList[i].get_price() > askentry.get_price():
                self.AskList.insert(i, askentry)
                if i == 0:
                    self.AskPrice = askentry.get_price()
        if len(self.BidList) == 0:
            self.BidList.append(entry)
        if len(self.AskList) == 0:
            self.AskList.append(askentry)

    def clean_lists(self):
        if len(self.AskList) == 0 or len(self.BidList) == 0:
            self.AskList = []
            self.BidList = []
            return
        for i in range(0, len(self.BidList)):
            if self.BidList[i].get_price() < self.AskPrice:
                self.BidList = self.BidList[:i]
                break
        for i in range(0, len(self.AskList)):
            if self.AskList[i].get_price() > self.BidPrice:
                self.AskList = self.AskList[:i]
                break
        if len(self.BidList) == 0:
            self.BidPrice = 0
        if len(self.AskList) == 0:
            self.AskPrice = 0

    def print_bids(self):
        if len(self.BidList) == 0 or len(self.AskList) == 0:
            return
        for bid in self.BidList:
            bidval = bid.get_price()
            bestaskval = self.AskList[0].get_price()
            worstaskval = self.AskList[-1].get_price()
            percent = 100 * bidval / bestaskval
            lowpercent = 100 * bidval / worstaskval
            print("Bid ",bid.Symbol," on ",bid.Exchange.id," is ","%.3f" % percent,
                  " of lowest ask on ",self.AskList[0].Exchange.id," and ",
                  "%.3f" % lowpercent," of highest ask on ", self.AskList[-1].Exchange.id)

    def print_test(self):
        print(self.Symbol+" - Bid[0]: "+str(self.BidList[0].Price)+", Bid[n]: "+str(self.BidList[-1].Price)+
              ", Ask[0]: "+str(self.AskList[0].Price)+", Ask[n]: "+str(self.AskList[-1].Price))