import botutils
import botconfig
import copy

bookbuffer = botconfig.order_book_trade_buffer

class Exchange:


    def __init__(self, ex):
        self.Ex = ex
        self.Markets = ex.load_markets()
        self.ID = ex.id
        self.Pairs = set()
        self.Currencies = {}
        self.OrderBooks = {}
        self.WithdrawLimits = copy.deepcopy(botconfig.withdraw_limits[self.ID])

    def add_pair(self, pair):

        self.Pairs.add(pair)

    def add_currency(self, currency):

        self.Currencies[currency.id] = currency

    def add_book(self, book, symbol):

        self.OrderBooks[symbol] = book

    def max_withdraw(self, currency, converted=False):

        #returns the maximum amount of a currency that can be withdrawn at the time of calling
        #TODO: get file records to find withdraw records from last 24 hours

        if type(self.WithdrawLimits) is dict:
            if currency in [*self.WithdrawLimits]:
                return self.WithdrawLimits[currency]
            else:
                if 'BTC' in [*self.WithdrawLimits]:
                    return self.convert_simple(self.WithdrawLimits['BTC'], 'BTC', currency)
                else:
                    if 'USD' in [*self.WithdrawLimits]:
                        return botutils.convert_from_USD(self.WithdrawLimits['USD'], currency, sigma=-0.05)
                    else:
                        return self.convert_simple(self.WithdrawLimits[[*self.WithdrawLimits][0]], [*self.WithdrawLimits][0], currency)

        return self.convert(self.WithdrawLimits, 'BTC', currency)

    def max_order_size(self, symbol, buysell, converted=True, sigma=bookbuffer):

        #returns the sum amount of base currency in all orders listed on the l2 order book

        book = self.OrderBooks[symbol]

        if buysell == 'buy':
            sum = 0.0
            for i in range(sigma, len(book['bids'])):
                sum += book['bids'][i][1]

            #print(sum)

        else:
            sum = 0.0
            for i in range(sigma, len(book['asks'])):
                if converted:
                    sum += book['asks'][i][0]*book['asks'][i][1]
                else:
                    sum += book['asks'][i][1]


        return sum

    def convert(self, amount, cfrom, cto, includefees=False, sigma=bookbuffer):

        #returns the converted value of 'amount' units of currency 'cfrom' in currency 'cto'
        #if there isn't a direct conversion, it tries to find intermediate conversions trough BTC, ETH, and USDT.
        #if no conversion is found, returns infinity.

        if cfrom == cto:
            return amount

        if cfrom+'/'+cto in [*self.Markets]:
            symbol = cfrom+'/'+cto
            fees = self.Markets[symbol]['taker'] if includefees else 0
            return self.market_buy(symbol, amount, sigma=sigma) * (1-fees)

        if cto+'/'+cfrom in [*self.Markets]:
            symbol = cto + '/' + cfrom
            fees = self.Markets[symbol]['taker'] if includefees else 0
            return self.market_sell(symbol, amount, sigma=sigma) * (1 - fees)

        if cfrom != 'BTC':

            if cfrom+'/BTC' in [*self.Markets]:

                symbol = cfrom+'/BTC'
                fees = self.Markets[symbol]['taker'] if includefees else 0
                return self.convert(self.market_buy(symbol, amount, sigma=sigma)*(1-fees), 'BTC', cto, includefees, sigma=sigma)

            else:
                if ('BTC/'+cfrom) in [*self.Markets]:
                    symbol = 'BTC/'+cfrom
                    fees = self.Markets[symbol]['taker'] if includefees else 0
                    return self.convert(self.market_sell(symbol, amount, sigma=sigma) * (1 - fees), 'BTC', cto, includefees, sigma=sigma)

        if cfrom != 'ETH':

            if cfrom + '/ETH' in [*self.Markets]:
                symbol = cfrom + '/ETH'
                fees = self.Markets[symbol]['taker'] if includefees else 0
                return self.convert(self.market_buy(symbol, amount, sigma=sigma) * (1 - fees), 'ETH', cto, includefees, sigma=sigma)

            else:
                if ('ETH/' + cfrom) in [*self.Markets]:
                    symbol = 'ETH/' + cfrom
                    fees = self.Markets[symbol]['taker'] if includefees else 0
                    return self.convert(self.market_sell(symbol, amount, sigma=sigma) * (1 - fees), 'ETH', cto, includefees, sigma=sigma)

        if cfrom != 'USDT':

            if cfrom + '/USDT' in [*self.Markets]:
                symbol = cfrom + '/USDT'
                fees = self.Markets[symbol]['taker'] if includefees else 0
                return self.convert(self.market_buy(symbol, amount, sigma=sigma) * (1 - fees), 'USDT', cto, includefees, sigma=sigma)

            else:

                if ('USDT/' + cfrom) in [*self.Markets]:
                    symbol = 'USDT/' + cfrom
                    fees = self.Markets[symbol]['taker'] if includefees else 0
                    return self.convert(self.market_sell(symbol, amount, sigma=sigma) * (1 - fees), 'USDT', cto, includefees, sigma=sigma)

        return float('inf')

    def convert_simple(self, amount, cfrom, cto, includefees=False, sigma=bookbuffer):
        #returns the converted value of 'amount' units of currency 'cfrom' in currency 'cto'
        #if there isn't a direct conversion, it tries to find intermediate conversions trough BTC, ETH, and USDT.
        #if no conversion is found, returns infinity.

        if cfrom == cto:
            return amount

        if cfrom+'/'+cto in [*self.Markets]:
            symbol = cfrom+'/'+cto
            fees = self.Markets[symbol]['taker'] if includefees else 0
            return self.ask(symbol)*amount*(1 - fees)

        if cto+'/'+cfrom in [*self.Markets]:
            symbol = cto + '/' + cfrom
            fees = self.Markets[symbol]['taker'] if includefees else 0
            return amount/self.bid(symbol)*(1 - fees)

        if cfrom != 'BTC':

            if cfrom+'/BTC' in [*self.Markets]:

                symbol = cfrom+'/BTC'
                fees = self.Markets[symbol]['taker'] if includefees else 0
                return self.convert_simple(self.ask(symbol)*amount*(1 - fees), 'BTC', cto, includefees, sigma=sigma)

            else:
                if ('BTC/'+cfrom) in [*self.Markets]:
                    symbol = 'BTC/'+cfrom
                    fees = self.Markets[symbol]['taker'] if includefees else 0
                    return self.convert_simple(amount/self.bid(symbol)*(1 - fees), 'BTC', cto, includefees, sigma=sigma)

        if cfrom != 'ETH':

            if cfrom + '/ETH' in [*self.Markets]:
                symbol = cfrom + '/ETH'
                fees = self.Markets[symbol]['taker'] if includefees else 0
                return self.convert_simple(self.ask(symbol)*amount*(1 - fees), 'ETH', cto, includefees, sigma=sigma)

            else:
                if ('ETH/' + cfrom) in [*self.Markets]:
                    symbol = 'ETH/' + cfrom
                    fees = self.Markets[symbol]['taker'] if includefees else 0
                    return self.convert_simple(amount/self.bid(symbol)*(1 - fees), 'ETH', cto, includefees, sigma=sigma)

        if cfrom != 'USDT':

            if cfrom + '/USDT' in [*self.Markets]:
                symbol = cfrom + '/USDT'
                fees = self.Markets[symbol]['taker'] if includefees else 0
                return self.convert_simple(self.ask(symbol)*amount*(1 - fees), 'USDT', cto, includefees, sigma=sigma)

            else:

                if ('USDT/' + cfrom) in [*self.Markets]:
                    symbol = 'USDT/' + cfrom
                    fees = self.Markets[symbol]['taker'] if includefees else 0
                    return self.convert_simple(amount/self.bid(symbol)*(1 - fees), 'USDT', cto, includefees, sigma=sigma)

        return float('inf')

    def bid(self, symbol):
        if symbol in [*self.OrderBooks] and len(self.OrderBooks[symbol]['bids']) > 0:
            return self.OrderBooks[symbol]['bids'][0][0]
        return -float('inf')

    def ask(self, symbol):
        if symbol in [*self.OrderBooks] and len(self.OrderBooks[symbol]['asks']) > 0:
            return self.OrderBooks[symbol]['asks'][0][0]
        return float('inf')

    def estimate_bid_price(self, symbol, amount, sigma=bookbuffer):

        #estimate the price of buying the listed amount of currency based on the orders in the market's order book
        #symbol and amount are as expected, sigma is the skips past the current bid price to account for orders filled
        #since the last time market data was queried.

        assert symbol in [*self.Markets] #convert to get_market call

        book = self.OrderBooks[symbol]

        if sigma > len(book['bids']):
            return -float('inf')

        if amount <= 0:
            return book['bids'][sigma][0]

        i = sigma
        count = 0
        price = 0
        while count < amount:
            #min value in quote currency
            minval = min(amount - count, book['bids'][i][1]*book['bids'][i][0])
            #count in quote
            count += minval
            #price in base
            price += minval/book['bids'][i][0]
            i +=1
            if i == len(book['bids']) and count != amount:
                print(count, '..... ', price)
                return -1
        return price/amount

    def estimate_sell_price(self, symbol, amount, sigma=bookbuffer):

        # estimate the price of buying the listed amount of currency based on the orders in the market's order book
        # symbol and amount are as expected, sigma is the skips past the current bid price to account for orders filled
        # since the last time market data was queried.

        assert symbol in [*self.Markets]  # convert to get_market call

        book = self.OrderBooks[symbol]

        if sigma > len(book['bids']):
            return -float('inf')

        if amount <= 0:
            return book['bids'][sigma][0]

        i = sigma
        count = 0
        price = 0
        while count < amount:
            # min value in quote currency
            minval = min(amount - count, book['asks'][i][1] * book['asks'][i][0])
            # count in quote
            count += minval
            # price in base
            price += minval / book['asks'][i][0]
            i += 1
            if i == len(book['asks']) and count != amount:
                print(count, '.... ', price)
                return -1
        return price / amount

    def estimate_sell_price_at(self, symbol, amount, sigma=bookbuffer):

        # estimate the price of buying the listed amount of currency based on the orders in the market's order book
        # symbol and amount are as expected, sigma is the skips past the current bid price to account for orders filled
        # since the last time market data was queried.

        assert symbol in [*self.Markets]  # convert to get_market call

        book = self.OrderBooks[symbol]

        if sigma > len(book['bids']):
            return -float('inf')

        if amount <= 0:
            return book['bids'][sigma][0]

        i = sigma
        count = 0
        price = 0
        while count < amount:
            # min value in quote currency
            minval = min(amount - count, book['asks'][i][1] * book['asks'][i][0])
            # count in quote
            count += minval
            # price in base
            price = book['asks'][i][0]
            i += 1
            if i == len(book['asks']) and count != amount:

                print(count, '.... ', price)
                return -1
        return price

    def estimate_buy_price(self, symbol, amount, sigma=bookbuffer):

        assert symbol in [*self.Markets]  # convert to get_market call

        book = self.OrderBooks[symbol]

        if sigma > len(book['bids']):
            return -float('inf')

        if amount <= 0:
            return book['bids'][sigma][0]

        i = sigma
        count = 0
        price = 0
        while count < amount:
            minval = min(amount - count, book['bids'][i][1])
            count += minval
            price += minval * book['bids'][i][0]
            i += 1
            if i == len(book['bids']) and count != amount:
                print(count, '... ', price)
                return -1

        return price/amount

    def estimate_buy_price_at(self, symbol, amount, sigma=bookbuffer):

        assert symbol in [*self.Markets]  # convert to get_market call

        book = self.OrderBooks[symbol]

        if sigma > len(book['bids']):
            return -float('inf')

        if amount <= 0:
            return book['bids'][sigma][0]

        i = sigma
        count = 0
        price = 0
        while count < amount:
            minval = min(amount - count, book['bids'][i][1])
            count += minval
            price = book['bids'][i][0]
            i += 1
            if i == len(book['bids']) and count != amount:
                print(count, '... ', price)
                return -1

        return price

    def estimate_ask_price(self, symbol, amount, sigma=bookbuffer):

        assert symbol in [*self.Markets]  # convert to get_market call

        book = self.OrderBooks[symbol]

        if sigma > len(book['bids']):
            return -float('inf')

        if amount <= 0:
            return book['asks'][sigma][0]

        i = sigma
        count = 0
        price = 0
        while count < amount:
            minval = min(amount - count, book['asks'][i][1])
            count += minval
            price += minval * book['asks'][i][0]
            i += 1
            if i == len(book['asks']) and count != amount:
                print('estimate-ask-price amount out of range')
                return -float('inf')
        return price/amount

    def estimate_bid_order(self, symbol, amount, amtqcurrency=False, sigma=bookbuffer):

        #estimate the price of buying the listed amount of currency based on the orders in the market's order book
        #symbol and amount are as expected, sigma is the skips past the current bid price to account for orders filled
        #since the last time market data was queried. Amtqcurrency is a flag for whether the amount provided is given in
        #the quote currency (True) or the base currency (False).

        assert symbol in [*self.Markets] #convert to get_market call

        if amount <= 0:
            return amount

        book = self.OrderBooks[symbol]

        if sigma > len(book['bids']):
            return -float('inf')

        i = sigma
        count = 0
        price = 0
        while count < amount:
            #min value in quote currency
            minval = min(amount - count, book['bids'][i][1]*book['bids'][i][0])
            #count in quote
            count += minval
            #price in base
            price += minval/book['bids'][i][0]
            i +=1
            if i == len(book['bids']) and count != amount:
                print(count, '. ', price)
                return -float('inf')
        return price

    def market_sell(self, symbol, amount, amtqcurrency=False, sigma=bookbuffer):

        #estimate the price of buying the listed amount of currency based on the orders in the market's order book
        #symbol and amount are as expected, sigma is the skips past the current bid price to account for orders filled
        #since the last time market data was queried. Amtqcurrency is a flag for whether the amount provided is given in
        #the quote currency (True) or the base currency (False).

        #note, the terminology is backwards on these, since the amount is the amount worth of X being sold.

        assert symbol in [*self.Markets] #convert to get_market call

        if amount <= 0:
            return amount

        book = self.OrderBooks[symbol]

        if sigma > len(book['asks']):
            return -float('inf')

        i = sigma
        count = 0
        price = 0
        k = 0

        while count < amount:
            #min value in quote currency
            minval = min(amount - count, book['asks'][i][1]*book['asks'][i][0])
            #count in quote
            count += minval
            #price in base
            price += minval/book['asks'][i][0]
            i +=1
            if i == len(book['asks']) and count != amount:
                print(book['asks'][i-1][0],'/',count, '/ ',amount,'/',price)
                #raise Exception
                return -float('inf')
        #print(count,',, ',price)
        return price

    def market_buy(self, symbol, amount, converted=True, sigma=bookbuffer):

        assert symbol in [*self.Markets]

        if amount <= 0:
            return amount

        book = self.OrderBooks[symbol]

        if sigma > len(book['bids']):
            return -float('inf')

        i = sigma
        count = 0
        price = 0
        while count < amount:
            minval = min(amount - count, book['bids'][i][1])
            count += minval

            price += minval * book['bids'][i][0]
            i += 1
            if i == len(book['bids']) and count != amount:
                print(count, ' ', price)
                return -float('inf')
        return price


    def estimate_ask_order(self, symbol, amount, sigma=bookbuffer):


        assert symbol in [*self.Markets]

        if amount <= 0:
            return amount

        book = self.OrderBooks[symbol]

        if sigma > len(book['bids']):
            return -float('inf')

        i = sigma
        count = 0
        price = 0
        while count < amount:
            minval = min(amount - count, book['asks'][i][1])
            count += minval
            price += minval * book['asks'][i][0]
            i += 1
            if i == len(book['asks']) and count != amount:
                print(count, ', ', price)
                return -1
        return price

    def estimate_sell_cost(self, symbol, amount, sigma=bookbuffer):

        #how much you'd need to sell to get X amount of the base currency

        assert symbol in [*self.Markets]

        if amount <= 0:
            return amount

        book = self.OrderBooks[symbol]

        if sigma > len(book['bids']):
            return float('inf')

        i = sigma
        count = 0
        price = 0
        while count < amount:
            # min value in quote currency
            minval = min(amount - count, book['asks'][i][1])
            # count in quote
            count += minval
            # price in base
            price += minval * book['asks'][i][0]
            i += 1
            if i == len(book['asks']) and count != amount:
                #print(count, ',,, ', price)
                return float('inf')
        return price

    def estimate_buy_cost(self, symbol, amount, sigma=bookbuffer):

        #how much buying X amount of the quote currency costs

        assert symbol in [*self.Markets]

        if amount <= 0:
            return amount

        book = self.OrderBooks[symbol]

        if sigma > len(book['bids']):
            return float('inf')

        i = sigma
        count = 0
        price = 0
        while count < amount:
            minval = min(amount - count, book['bids'][i][0]*book['bids'][i][1])
            count += minval
            price += book['bids'][i][1]
            i += 1
            if i == len(book['bids']) and count != amount:
                #print(count, ',,,, ', price)
                return float('inf')

        return price
