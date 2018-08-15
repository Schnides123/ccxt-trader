import Transaction
import ccxt
import queue
import copy

class TransactionChain:

    def __init__(self, balance):

        self.Transactions = queue.Queue()
        self.Balance = balance
        self.Pending = None
        self.Started = False
        self.Finished = False

    def size(self):

        return self.Transactions.qsize()

    def set(self, txchain):

        self.Transactions = copy.deepcopy(txchain.Transactions)

    def start(self):

        if self.validate_chain() == False:
            raise Exception("Invalid Transaction Chain")

        if self.Transactions.qsize() == 0:
            self.Finished = True
            return
        if self.Started:
            self.update()
            return
        self.Started = True
        self.Pending = self.Transactions.get()
        self.Pending.push_tx()

    def update(self):

        if not self.Started:
            self.start()
            return

        if self.Finished or not self.Pending.Finished:
            return

        if self.Pending.Finished:
            if self.Transactions.qsize() == 0:
                self.Finished = True
                return
            self.Pending = self.Transactions.get()
            self.Pending.push_tx()

    def validate_chain(self):

        #TODO:
        #for tx in transactions
        #if cfrom != last.cto or efrom != last.eto or amount > last.amount return false
        # else return true
