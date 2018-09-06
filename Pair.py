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
            self.ExBuy = None
            self.Exsell = None
            #print('Null exchange')
            #print(symbol)
            return
        if ex1.bid(symbol) > ex2.ask(symbol):
            self.Exsell = ex1
            self.ExBuy = ex2
        else:
            if ex2.bid(symbol) > ex1.ask(symbol):
                self.Exsell = ex2
                self.ExBuy = ex1
            else:
                self.ExBuy = None
                self.Exsell = None
                return

        if not (self.Base in [*self.ExBuy.Ex.fees['funding']['withdraw']] and self.Quote in [*self.Exsell.Ex.fees['funding']['withdraw']]):
            self.ExBuy = None
            self.Exsell = None
            #print('no fee information available')
            return

        # percentage fees given in the form of a decimal ranging from [0, 1] for 0 to 100%
        self.PercentFees = {'buy': self.ExBuy.Markets[symbol]['taker'], 'sell': self.Exsell.Markets[symbol]['taker']}

        self.FlatFees = {}

        #Bit-Z can eat a dick
        if type(self.ExBuy.Ex.fees['funding']['withdraw'][self.Base]) == str and self.ExBuy.Ex.fees['funding']['withdraw'][self.Base][-1] == '%':
            self.PercentFees['buy'] += float(self.ExBuy.Ex.fees['funding']['withdraw'][self.Base][0:-1])/100.0
            self.FlatFees['buy'] = 0
        else:
            self.FlatFees['buy'] = self.ExBuy.Ex.fees['funding']['withdraw'][self.Base]

        if type(self.Exsell.Ex.fees['funding']['withdraw'][self.Quote]) == str and self.Exsell.Ex.fees['funding']['withdraw'][self.Quote][-1] == '%':
            self.PercentFees['sell'] += float(self.Exsell.Ex.fees['funding']['withdraw'][self.Quote][0:-1]) / 100.0
            self.FlatFees['sell'] = 0
        else:
            self.FlatFees['sell'] = self.Exsell.Ex.fees['funding']['withdraw'][self.Quote]

        #flat costs of trade in converted to base currency
        #self.FlatFees = {'buy' : self.ExBuy.Ex.fees['funding']['withdraw'][self.Base] , 'sell' : self.Exsell.Ex.fees['funding']['withdraw'][self.Quote]}


        #approximate profit margin in decimal form based on latest sell and buy prices.
        self.Margin = self.Exsell.bid(symbol)/self.ExBuy.ask(symbol)
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

        sellmax = self.Exsell.max_order_size(self.Symbol, 'sell')
        buymax = self.ExBuy.max_order_size(self.Symbol, 'buy', converted=True)
        # print(sellmax, self.ExBuy.market_buy(self.Symbol, buymax), buymax, self.Exsell.market_sell(self.Symbol, sellmax))

        sellmaxadj = min(sellmax, self.Exsell.estimate_sell_cost(self.Symbol, buymax))
        buymaxadj = self.ExBuy.market_buy(self.Symbol,
                                             min(buymax, self.ExBuy.estimate_buy_cost(self.Symbol, sellmax)))
        mcount = min(sellmaxadj, buymaxadj)
        #sellmax = self.Exsell.max_order_size(self.Symbol, 'sell')
        #buymax = self.ExBuy.max_order_size(self.Symbol, 'buy', converted=True)
        #sellmaxadj = min(sellmax, self.ExBuy.market_buy(self.Symbol, buymax))
        #buymaxadj = self.ExBuy.market_buy(self.Symbol, min(buymax, self.Exsell.market_sell(self.Symbol, sellmax)))
        #mcount = min(sellmaxadj, buymaxadj)
        sbook = self.Exsell.OrderBooks[self.Symbol]
        bbook = self.ExBuy.OrderBooks[self.Symbol]


        scount = 0
        bcount = 0
        lcount = 0
        ai = sigma
        bi = sigma
        if sigma >= len(sbook['bids']) or sigma >= len(bbook['asks']):
            return float('inf')

        sprice = sbook['bids'][ai][0]
        bprice = bbook['asks'][bi][0]

        if self.FlatFees['sell'] == 0 and self.FlatFees['buy'] == 0 and sprice > bprice:
            #print('no fees')
            return 0

        #todo: test this hacky garbage
        if self.Margin <= 1:
            #print('Margin < 1')
            return float('inf')

        #bprice starts above sprice, and
        while min(scount, bcount) < mcount and ai < len(sbook['bids']) and bi < len(
                bbook['asks']):
            lcount = min(scount, bcount)
            lprice = sprice-bprice
            if scount+self.FlatFees['sell']/self.Exsell.estimate_sell_price(self.Symbol, scount, sigma=sigma) < bcount+self.FlatFees['sell']:
                scount += sbook['bids'][ai][1]
                sprice = sbook['bids'][ai][0] * (1 - self.PercentFees['sell'])
                ai += 1
            else:
                bcount += bbook['asks'][bi][1]
                bprice = bbook['asks'][bi][0] * (1 + self.PercentFees['buy'])
                bi += 1
            if min(scount, bcount) > mcount:
                print('order book overflow')
                return float('inf')
            #print(min(scount, bcount), mcount, buymax, sellmax)
            rmin = self.roi(min(scount, bcount), sellbuy='sell', flatfee=flatfee, percentfee=percentfee)
            rlast = self.roi(lcount, sellbuy='sell', flatfee=flatfee, percentfee=percentfee)
            if rmin >= 0:

                if rmin == 0:
                    return min(scount, bcount)
                #print(lcount + (lcount - rlast / (rmin - rlast) * (min(scount, bcount) - lcount) * (sprice - bprice)))
                #print(sprice, bprice, lprice, -rlast / (rmin - rlast) * (min(scount, bcount) - lcount)*lprice)
                #todo: fix this
                #a = (lcount + ((min(scount, bcount) - lcount)*rmin/(rmin-rlast)))
                #b = (lcount - rlast/(rmin-rlast)*(min(scount, bcount)-lcount)*(sprice-bprice))
                #c = lcount + abs(rlast/rmin)*(min(scount, bcount) - lcount)/(1+min(scount, bcount) - lcount)
                #print(self.roi(a), self.roi(b), self.roi(c))
                #print('min: ',lcount + (lcount - rlast / (rmin - rlast) * (min(scount, bcount) - lcount) * (sprice - bprice)))


                return max(lcount + (lcount - rlast/(rmin-rlast)*(min(scount, bcount)-lcount)*(sprice-bprice)), 0)


        #print('loop overrun')
        #print(max(scount, bcount) < mcount, ai < len(sbook['bids']), bi < len(
        #    bbook['asks']))
        return float('inf')


    def max_trade(self, percentfee=0, sigma=bookbuffer, error=0.01):

        #cases:
        # sell max >  buy max
        # buy max > sellmax
        # if sell max > buy max, buy max has to be set to back-converted sell max
        # if buy max > sellmax, sellmax has to be set to back-converted buymax
        # if sellmax > buy max sellmax backconverted will give inf
        # if buymax > sellmax, buymax backconverted will give inf
        #
        #

        sellmax = self.Exsell.max_order_size(self.Symbol, 'sell')
        buymax = self.ExBuy.max_order_size(self.Symbol, 'buy', converted=True)
        #print(sellmax, self.ExBuy.market_buy(self.Symbol, buymax), buymax, self.Exsell.market_sell(self.Symbol, sellmax))

        sellmaxadj = min(sellmax, self.Exsell.estimate_sell_cost(self.Symbol, buymax))
        buymaxadj = self.ExBuy.market_buy(self.Symbol, min(buymax, self.ExBuy.estimate_buy_cost(self.Symbol, sellmax)))
        mcount = min(sellmaxadj, buymaxadj)
        if abs(mcount) == float('inf'):
            print("!!!!")
        #print(sellmaxadj, buymaxadj, sellmaxadj2, buymaxadj2)

        # print(sellmaxadj, buymaxadj, sellmax, buymax,(mcount), self.ExBuy.max_order_size(self.Symbol, 'buy', converted=False))
        #
        # print(sellmax, buymax, sellmaxadj, buymaxadj)
        # print(self.ExBuy.estimate_buy_cost(self.Symbol, sellmax))
        # print(self.Exsell.estimate_sell_cost(self.Symbol, buymax))
        # print(self.ExBuy.market_buy(self.Symbol, buymax))
        # print(self.Exsell.market_sell(self.Symbol, sellmax))
        # print('test')

        #print(self.roi(self.Exsell.market_sell(self.Symbol, mcount), sellbuy='sell'))

        #sellmaxadj = sellmax*self.Exsell.estimate_sell_price(self.Symbol, sellmax) * self.ExBuy.estimate_buy_price(self.Symbol, buymax)
        #buymaxadj = buymax * self.Exsell.estimate_sell_price(self.Symbol, sellmax) * self.ExBuy.estimate_buy_price(
        #self.Symbol, buymax)#

        #print(sellmaxadj, buymaxadj, self.Exsell.estimate_sell_price(self.Symbol, sellmax) * self.ExBuy.estimate_buy_price(self.Symbol, buymax))
        sbook = self.Exsell.OrderBooks[self.Symbol]
        bbook = self.ExBuy.OrderBooks[self.Symbol]

        scount = 0
        bcount = 0
        lcount = 0
        smax = float('inf')
        bmax = -float('inf')
        ai = sigma
        bi = sigma
        if sigma >= len(sbook['bids']) or sigma >= len(bbook['asks']):
            return -1
        sprice = sbook['bids'][ai][0]
        bprice = bbook['asks'][bi][0]

        while min(scount, bcount) < mcount and smax > bmax and ai < len(sbook['bids']) and bi < len(bbook['asks']):


            lcount = min(scount, bcount)
            if scount < bcount:
                scount += sbook['bids'][ai][1]
                sprice = sbook['bids'][ai][0] * (1 - self.PercentFees['buy'])
                ai+=1

            else:
                bcount += bbook['asks'][bi][1]
                bprice = bbook['asks'][bi][0] * (1 + self.PercentFees['sell'])
                bi+=1





            #print(scount, bcount, mcount, min(scount, bcount) < mcount, sprice < bprice, ai < len(sbook['bids']) and bi < len(bbook['asks']), sprice, bprice)

            #smax= self.Exsell.estimate_sell_price_at(self.Symbol, min(,min(scount, bcount)) * (1 - self.PercentFees['buy'] - percentfee)
            #bmax = self.ExBuy.estimate_buy_price_at(self.Symbol, min(sum(bbook['asks'][:][1]),max(scount, bcount)) * (1 + self.PercentFees['$sell$'])
            smax = self.Exsell.estimate_sell_price_at(self.Symbol, min(scount, bcount)) * (1 - self.PercentFees['sell'] - percentfee)
            bmax = self.ExBuy.estimate_buy_price_at(self.Symbol, self.Exsell.market_sell(self.Symbol, min(scount, bcount))) * (1 + self.PercentFees['buy'])
        #print('maxmargin:')
        #print(lcount > mcount)
        #print(self.roi(lcount, sellbuy='sell'))
        return lcount #, self.Exsell.convert_simple(self.Exsell.max_withdraw(self.Quote), self.Quote, self.Base), self.ExBuy.max_withdraw(self.Base))



    def margin(self, amount, flatfee=0, percentfee=0, sigma=bookbuffer):
        #amount, fees is expressed in base currency

        # amt = amount * (1-percentfee) - flatfee
        # first = self.ExBuy.market_buy(self.Symbol, amt)*(1-self.PercentFees['buy'])-self.FlatFees['buy']
        # second = self.Exsell.market_sell(self.Symbol, first)*(1 - self.PercentFees['sell']) - self.FlatFees['sell'] / self.Exsell.estimate_sell_price(
        #     self.Symbol, amount, sigma=sigma)

        print(self.FlatFees)


        amt = amount * (1 - percentfee) - flatfee
        first = self.ExBuy.market_buy(self.Symbol, amt) if amt > 0 else amt - self.PercentFees['buy'] * abs(amt) - \
                                                                          self.FlatFees['buy']
        second = self.Exsell.market_sell(self.Symbol, first) if amt > 0 else first - self.PercentFees['sell'] * abs(
            first) - self.FlatFees[
                                                                               'sell'] / self.Exsell.estimate_sell_price(
            self.Symbol, first, sigma=sigma)

        return second/amount if amount != 0 else 0

    def roi(self, amount, sellbuy='buy', flatfee=0, percentfee=0, sigma=bookbuffer):

        #amount is given in base currency, sold to the quote currency, and bought back as the base


        if sellbuy == 'sell':

            amt = amount * (1-percentfee) - flatfee
            if amt > self.Exsell.max_order_size(self.Symbol, 'sell'):
                print('above max')
                return -float('inf')
            
            sold = (self.Exsell.market_sell(self.Symbol, amt - self.PercentFees['sell']*abs(amt)) if amt > 0 else amt) - self.FlatFees['sell']
            # /self.Exsell.estimate_sell_price(self.Symbol, first, sigma=sigma))
            #todo : double check and test fee conversion
            #print('test',amount,first)
            bought = (self.ExBuy.market_buy(self.Symbol, sold - self.PercentFees['buy'] * abs(
                sold)) if amt > 0 else sold) - self.FlatFees['buy']

            #print('amt', amt, self.ExBuy.estimate_buy_cost(self.Symbol, sold))
            #print('first', sold, self.Exsell.estimate_sell_cost(self.Symbol, bought))
            #print('second', bought, amount, self.FlatFees['sell'], self.FlatFees[
            #   'sell'])
            #print('test2',amount,first,second)
            return bought - amount

        #amount is given in qupte currency, bought to base, and sold back to quote

        amt = amount * (1 - percentfee) - flatfee
        if amt > self.ExBuy.max_order_size(self.Symbol, 'buy'):
            print('above max')
            return -float('inf')
        #print(amt, self.ExBuy.max_order_size(self.Symbol, 'buy'))
        first = ( self.ExBuy.market_buy(self.Symbol, amt) if amt > 0 else amt ) - self.PercentFees['buy']*abs(amt) - self.FlatFees['buy']

        #print('amt', amt, self.ExBuy.estimate_buy_cost(self.Symbol, first))

        ##print(first)
        second = ( self.Exsell.market_sell(self.Symbol, first) if amt > 0 else first ) - self.PercentFees['sell']*abs(first) - self.FlatFees[
            'sell'] #/ self.Exsell.estimate_sell_price(self.Symbol, first, sigma=sigma)
        ##print(second)
        ##print('****')
        #print('first', first, self.Exsell.estimate_sell_cost(self.Symbol, second))
        #print('second', second, amount, self.FlatFees['sell'], self.FlatFees[
        #    'sell'])#/self.Exsell.estimate_sell_price(self.Symbol, first, sigma=sigma))
        return second - amount


    def __str__(self):
        return 'sell: '+self.Exsell.Ex.name+', buy:'+self.ExBuy.Ex.name+', via '+self.Symbol+' | '+'%.3f' % (100*self.Margin-100)+'% | min: '+"%.5f" % self.min_trade()+' | max: '+'%.5f'%self.max_trade()+' | $'+"%.2f" % botutils.convert_to_USD(self.max_trade(), self.Base)+' -> $'+"%.2f" % botutils.convert_to_USD(self.max_trade()+self.roi(self.max_trade(), sellbuy='sell'), self.Base)