import botutils
import botconfig

class Balance:

    def __init__(self, amount, currency, exchange=None):

        self.Amount = amount
        self.Exchange = exchange
        self.Currency = currency
        self.TxChain = None
        self.InWallet = exchange == None

    def amountUSD(self):
        return botutils.convert_to_USD(self.Amount, self.Currency)

    def assign_transactions(self, txchain):

        assert self.TxChain == None

        self.TxChain = txchain


    def is_allocated(self):

        return self.TxChain != None


    def split(self, n):

        newbal = Balance(self.Amount - n, self.Exchange, self.Currency)
        self.Amount = n
        return newbal

    def balance_key(self):

        return self.Currency.id + "@w" if self.InWallet else self.Exchange.ID