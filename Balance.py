class Balance:

    def __init__(self, amount, exchange, currency):

        self.Amount = amount
        self.AmountUSD #TODO
        self.Exchange = exchange
        self.Currency = currency
        self.TxChain = None
        self.InWallet = exchange == None

    def __init__(self, amount, currency):

        self.Amount = amount
        self.AmountUSD
        self.Exchange = None
        self.Currency = currency
        self.TxChain = None
        self.InWallet = True

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

        return self.Currency.id + "@w" if self.InWallet else self.Exchange.id