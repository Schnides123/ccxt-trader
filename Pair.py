import botutils
import botconfig

bookbuffer = botconfig.order_book_trade_buffer

class Pair:

    def __init__(self, ex1, ex2, symbol):


        # calculate which exchange is cheaper, set from and to accordingly
        self.Symbol = symbol
        self.Base = botutils.base(symbol)
        self.Quote = botutils.quote(symbol)
        self.Margin = 0

        if not (symbol in [*ex1.OrderBooks] and symbol in [*ex2.OrderBooks]):
            self.ExSell = None
            self.ExBuy = None
            #print('Null exchange')
            #print(symbol)
            return
        if ex1.bid(symbol) > ex2.ask(symbol):
            self.ExBuy = ex1
            self.ExSell = ex2
        else:
            if ex2.bid(symbol) > ex1.ask(symbol):
                self.ExBuy = ex2
                self.ExSell = ex1
            else:
                self.ExSell = None
                self.ExBuy = None
                return

        if not (self.Base in [*self.ExSell.Ex.fees['funding']['withdraw']] and self.Quote in [*self.ExBuy.Ex.fees['funding']['withdraw']]):
            self.ExSell = None
            self.ExBuy = None
            #print('no fee information available')
            return

        # percentage fees given in the form of a decimal ranging from [0, 1] for 0 to 100%
        self.PercentFees = {'sell': self.ExSell.Markets[symbol]['taker'], 'buy': self.ExBuy.Markets[symbol]['taker']}

        self.FlatFees = {}

        #Bit-Z can eat a dick
        if type(self.ExSell.Ex.fees['funding']['withdraw'][self.Base]) == str and self.ExSell.Ex.fees['funding']['withdraw'][self.Base][-1] == '%':
            self.PercentFees['sell'] += float(self.ExSell.Ex.fees['funding']['withdraw'][self.Base][0:-1])/100.0
            self.FlatFees['sell'] = 0
        else:
            self.FlatFees['sell'] = self.ExSell.Ex.fees['funding']['withdraw'][self.Base]

        if type(self.ExBuy.Ex.fees['funding']['withdraw'][self.Quote]) == str and self.ExBuy.Ex.fees['funding']['withdraw'][self.Quote][-1] == '%':
            self.PercentFees['buy'] += float(self.ExBuy.Ex.fees['funding']['withdraw'][self.Quote][0:-1]) / 100.0
            self.FlatFees['buy'] = 0
        else:
            self.FlatFees['buy'] = self.ExBuy.Ex.fees['funding']['withdraw'][self.Quote]

        #flat costs of trade in converted to base currency
        #self.FlatFees = {'sell' : self.ExSell.Ex.fees['funding']['withdraw'][self.Base] , 'buy' : self.ExBuy.Ex.fees['funding']['withdraw'][self.Quote]}


        #approximate profit margin in decimal form based on latest buy and sell prices.
        self.Margin = self.ExBuy.bid(symbol)/self.ExSell.ask(symbol)
        #if self.Margin > 1.01:
        #    print(str(self), ' | min: ', self.min_trade(), ' | max: ', self.max_trade())

        ##  print('test!')
        #if self.Margin > 1.01:
            #print(self.min_trade(), self.max_trade(), self.Margin)

        if self.Margin > 1.01:
            print(self)

        if self.min_trade() < self.max_trade():
            #print(self.roi(self.min_trade()))
            ex1.add_pair(self)
            ex2.add_pair(self)

        ##print('---')

    def min_trade(self, flatfee=0, percentfee=0, sigma=bookbuffer, error=0.0001000000001):

        buymax = self.ExBuy.max_order_size(self.Symbol, 'buy')
        sellmax = self.ExSell.max_order_size(self.Symbol, 'sell', converted=True)
        # print(buymax, self.ExSell.market_sell(self.Symbol, sellmax), sellmax, self.ExBuy.market_buy(self.Symbol, buymax))

        buymaxadj = min(buymax, self.ExBuy.estimate_buy_cost(self.Symbol, sellmax))
        sellmaxadj = self.ExSell.market_sell(self.Symbol,
                                             min(sellmax, self.ExSell.estimate_sell_cost(self.Symbol, buymax)))
        mcount = min(buymaxadj, sellmaxadj)
        #buymax = self.ExBuy.max_order_size(self.Symbol, 'buy')
        #sellmax = self.ExSell.max_order_size(self.Symbol, 'sell', converted=True)
        #buymaxadj = min(buymax, self.ExSell.market_sell(self.Symbol, sellmax))
        #sellmaxadj = self.ExSell.market_sell(self.Symbol, min(sellmax, self.ExBuy.market_buy(self.Symbol, buymax)))
        #mcount = min(buymaxadj, sellmaxadj)
        abook = self.ExBuy.OrderBooks[self.Symbol]
        bbook = self.ExSell.OrderBooks[self.Symbol]


        acount = 0
        bcount = 0
        lcount = 0
        ai = sigma
        bi = sigma
        if sigma >= len(abook['bids']) or sigma >= len(bbook['asks']):
            return float('inf')

        aprice = abook['bids'][ai][0]
        bprice = bbook['asks'][bi][0]

        if self.FlatFees['buy'] == 0 and self.FlatFees['sell'] == 0 and aprice > bprice:
            print('no fees')
            return 0

        #todo: test this hacky garbage
        if self.Margin <= 1:
            print('Margin < 1')
            return float('inf')

        #bprice starts above aprice, and
        while max(acount, bcount) < mcount and ai < len(abook['bids']) and bi < len(
                bbook['asks']):
            lcount = min(acount, bcount)
            lprice = aprice-bprice
            if acount+self.FlatFees['buy']/self.ExBuy.estimate_buy_price(self.Symbol, acount, sigma=sigma) < bcount+self.FlatFees['buy']:
                acount += abook['bids'][ai][1]
                aprice = abook['bids'][ai][0] * (1 - self.PercentFees['buy'])
                ai += 1
            else:
                bcount += bbook['asks'][bi][1]
                bprice = bbook['asks'][bi][0] * (1 + self.PercentFees['sell'])
                bi += 1
            if min(acount, bcount) > mcount:
                print('order book overflow')
                return float('inf')
            rmin = self.roi(min(acount, bcount), flatfee=flatfee, percentfee=percentfee)
            rlast = self.roi(lcount, flatfee=flatfee, percentfee=percentfee)
            if rmin >= 0:

                if rmin == 0:
                    return min(acount, bcount)
                #print(lcount + (lcount - rlast / (rmin - rlast) * (min(acount, bcount) - lcount) * (aprice - bprice)))
                #print(aprice, bprice, lprice, -rlast / (rmin - rlast) * (min(acount, bcount) - lcount)*lprice)
                #todo: fix this
                #a = (lcount + ((min(acount, bcount) - lcount)*rmin/(rmin-rlast)))
                #b = (lcount - rlast/(rmin-rlast)*(min(acount, bcount)-lcount)*(aprice-bprice))
                #c = lcount + abs(rlast/rmin)*(min(acount, bcount) - lcount)/(1+min(acount, bcount) - lcount)
                #print(self.roi(a), self.roi(b), self.roi(c))
                #print('min: ',lcount + (lcount - rlast / (rmin - rlast) * (min(acount, bcount) - lcount) * (aprice - bprice)))


                return max(lcount + (lcount - rlast/(rmin-rlast)*(min(acount, bcount)-lcount)*(aprice-bprice)), 0)


        print('loop overrun')
        print(max(acount, bcount) < mcount, ai < len(abook['bids']), bi < len(
            bbook['asks']))
        return float('inf')


    def max_trade(self, percentfee=0, sigma=bookbuffer, error=0.01):

        #cases:
        # Buy max >  sell max
        # sell max > buymax
        # if buy max > sell max, sell max has to be set to back-converted buy max
        # if sell max > buymax, buymax has to be set to back-converted sellmax
        # if buymax > sell max buymax backconverted will give inf
        # if sellmax > buymax, sellmax backconverted will give inf
        #
        #

        buymax = self.ExBuy.max_order_size(self.Symbol, 'buy')
        sellmax = self.ExSell.max_order_size(self.Symbol, 'sell', converted=True)
        #print(buymax, self.ExSell.market_sell(self.Symbol, sellmax), sellmax, self.ExBuy.market_buy(self.Symbol, buymax))

        buymaxadj = min(buymax, self.ExBuy.estimate_buy_cost(self.Symbol, sellmax))
        sellmaxadj = self.ExSell.market_sell(self.Symbol, min(sellmax, self.ExSell.estimate_sell_cost(self.Symbol, buymax)))
        mcount = min(buymaxadj, sellmaxadj)
        if abs(mcount) == float('inf'):
            print("!!!!")
        #print(buymaxadj, sellmaxadj, buymaxadj2, sellmaxadj2)

        # print(buymaxadj, sellmaxadj, buymax, sellmax,(mcount), self.ExSell.max_order_size(self.Symbol, 'sell', converted=False))
        #
        # print(buymax, sellmax, buymaxadj, sellmaxadj)
        # print(self.ExSell.estimate_sell_cost(self.Symbol, buymax))
        # print(self.ExBuy.estimate_buy_cost(self.Symbol, sellmax))
        # print(self.ExSell.market_sell(self.Symbol, sellmax))
        # print(self.ExBuy.market_buy(self.Symbol, buymax))
        # print('test')

        #print(self.roi(self.ExBuy.market_buy(self.Symbol, mcount), buysell='buy'))

        #buymaxadj = buymax*self.ExBuy.estimate_buy_price(self.Symbol, buymax) * self.ExSell.estimate_sell_price(self.Symbol, sellmax)
        #sellmaxadj = sellmax * self.ExBuy.estimate_buy_price(self.Symbol, buymax) * self.ExSell.estimate_sell_price(
        #self.Symbol, sellmax)#

        #print(buymaxadj, sellmaxadj, self.ExBuy.estimate_buy_price(self.Symbol, buymax) * self.ExSell.estimate_sell_price(self.Symbol, sellmax))
        abook = self.ExBuy.OrderBooks[self.Symbol]
        bbook = self.ExSell.OrderBooks[self.Symbol]

        acount = 0
        bcount = 0
        lcount = 0
        maxa = float('inf')
        maxb = -float('inf')
        ai = sigma
        bi = sigma
        if sigma >= len(abook['bids']) or sigma >= len(bbook['asks']):
            return -1
        aprice = abook['bids'][ai][0]
        bprice = bbook['asks'][bi][0]

        while min(acount, bcount) < mcount and maxa > maxb and ai < len(abook['bids']) and bi < len(bbook['asks']):


            lcount = min(acount, bcount)
            if acount < bcount:
                acount += abook['bids'][ai][1]
                aprice = abook['bids'][ai][0] * (1 - self.PercentFees['sell'])
                ai+=1

            else:
                bcount += bbook['asks'][bi][1]
                bprice = bbook['asks'][bi][0] * (1 + self.PercentFees['buy'])
                bi+=1





            #print(acount, bcount, mcount, min(acount, bcount) < mcount, aprice < bprice, ai < len(abook['bids']) and bi < len(bbook['asks']), aprice, bprice)

            #maxa = self.ExBuy.estimate_buy_price_at(self.Symbol, min(,min(acount, bcount)) * (1 - self.PercentFees['sell'] - percentfee)
            #maxb = self.ExSell.estimate_sell_price_at(self.Symbol, min(sum(bbook['asks'][:][1]),max(acount, bcount)) * (1 + self.PercentFees['buy'])
            maxa = self.ExBuy.estimate_buy_price_at(self.Symbol, min(acount, bcount)) * (1 - self.PercentFees['buy'] - percentfee)
            maxb = self.ExSell.estimate_sell_price_at(self.Symbol, self.ExBuy.market_buy(self.Symbol, min(acount, bcount))) * (1 + self.PercentFees['sell'])
        print('maxmargin:')
        print(self.roi(lcount))
        return lcount #, self.ExBuy.convert_simple(self.ExBuy.max_withdraw(self.Quote), self.Quote, self.Base), self.ExSell.max_withdraw(self.Base))



    def margin(self, amount, flatfee=0, percentfee=0, sigma=bookbuffer):
        #amount, fees is expressed in base currency

        # amt = amount * (1-percentfee) - flatfee
        # first = self.ExSell.market_sell(self.Symbol, amt)*(1-self.PercentFees['sell'])-self.FlatFees['sell']
        # second = self.ExBuy.market_buy(self.Symbol, first)*(1 - self.PercentFees['buy']) - self.FlatFees['buy'] / self.ExBuy.estimate_buy_price(
        #     self.Symbol, amount, sigma=sigma)

        print(self.FlatFees)


        amt = amount * (1 - percentfee) - flatfee
        first = self.ExSell.market_sell(self.Symbol, amt) if amt > 0 else amt - self.PercentFees['sell'] * abs(amt) - \
                                                                          self.FlatFees['sell']
        second = self.ExBuy.market_buy(self.Symbol, first) if amt > 0 else first - self.PercentFees['buy'] * abs(
            first) - self.FlatFees[
                                                                               'buy'] / self.ExBuy.estimate_buy_price(
            self.Symbol, first, sigma=sigma)

        return second/amount if amount != 0 else 0

    def roi(self, amount, buysell='sell', flatfee=0, percentfee=0, sigma=bookbuffer):

        ##print('testtest')
        #print(self.FlatFees)

        if buysell == 'buy':

            amt = amount * 1-percentfee - flatfee
            if amt > self.ExBuy.max_order_size(self.Symbol, 'buy'):
                print('above max')
                return -float('inf')
            first = ( self.ExBuy.market_buy(self.Symbol, amt - self.PercentFees['buy']*abs(amt)) if amt > 0 else amt) - self.FlatFees['buy']

            #print('test',amount,first)
            second = (self.ExSell.market_buy(self.Symbol, first - self.PercentFees['sell'] * abs(
                first)) if amt > 0 else first) - self.FlatFees['sell']
            #print('test2',amount,first,second)
            return second - amount

        amt = amount * (1 - percentfee) - flatfee
        if amt > self.ExSell.max_order_size(self.Symbol, 'sell'):
            print('above max')
            return -float('inf')
        #print(amt, self.ExSell.max_order_size(self.Symbol, 'sell'))
        first = ( self.ExSell.market_sell(self.Symbol, amt) if amt > 0 else amt ) - self.PercentFees['sell']*abs(amt) - self.FlatFees['sell']

        print('amt', amt, self.ExSell.estimate_sell_cost(self.Symbol, first))

        ##print(first)
        second = ( self.ExBuy.market_buy(self.Symbol, first) if amt > 0 else first ) - self.PercentFees['buy']*abs(first) - self.FlatFees[
            'buy'] #/ self.ExBuy.estimate_buy_price(self.Symbol, first, sigma=sigma)
        ##print(second)
        ##print('****')
        print('first', first, self.ExBuy.estimate_buy_cost(self.Symbol, second))
        print('second', second, amount, self.FlatFees['buy'], self.FlatFees[
            'buy'])#/self.ExBuy.estimate_buy_price(self.Symbol, first, sigma=sigma))
        return second - amount


    def __str__(self):
        return 'buy: '+self.ExBuy.Ex.name+', sell:'+self.ExSell.Ex.name+', via '+self.Symbol+' | '+'%.3f' % (100*self.Margin-100)+'% | min: '+"%.5f" % self.min_trade()+' | max: '+'%.5f'%self.max_trade()+' | $'+"%.2f" % botutils.convert_to_USD(self.max_trade(), self.Base)+' -> $'+"%.2f" % botutils.convert_to_USD(self.max_trade()+self.roi(self.max_trade()), self.Base)