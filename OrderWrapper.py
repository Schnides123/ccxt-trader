import CurrencyWrapper

class Order:

    def __init__(self, symbol, price, amount, exchange, id):
        self.Symbol = symbol
        self.Base = symbol.split("/")[0]
        self.Quote = symbol.split("/")[0]
        self.Price = price
        self.Amount = amount
        self.Exchange = exchange
        self.ID = id

    def check_status(self):
        try:
            if self.Exchange.has['fetch_order']:
                order = self.Exchange.fetch_order(self.ID)
                return order['status']
            else:
                return "unknown"
        except Exception as e:
            print(e)
            return "unknown"

