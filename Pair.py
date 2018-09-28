import botutils
import botconfig
import time

bookbuffer = botconfig.order_book_trade_buffer


class Pair:

    def __init__(self, ex1, ex2, symbol):

        self.Symbol = symbol
        self.Base = botutils.base(symbol)
        self.Quote = botutils.quote(symbol)
        self.Margin = 0

        if not (symbol in [*ex1.OrderBooks] and symbol in [*ex2.OrderBooks]):
            self.ExBuy = None
            self.ExSell = None
            return

        if ex1.bid(symbol) > ex2.ask(symbol):
            self.ExSell = ex1
            self.ExBuy = ex2
        else:
            if ex2.bid(symbol) > ex1.ask(symbol):
                self.ExSell = ex2
                self.ExBuy = ex1
            else:
                self.ExBuy = None
                self.ExSell = None
                return

        if not (self.Base in [*self.ExBuy.Ex.fees['funding']['withdraw']] and self.Quote in [*self.ExSell.Ex.fees['funding']['withdraw']]):
            if botconfig.require_fees:
                self.ExBuy = None
                self.ExSell = None
                return
            else:
                self.PercentFees = {'buy': botconfig.default_fee_percent, 'sell': botconfig.default_fee_percent}
                self.FlatFees = {'buy': 0, 'sell': 0}
        else:
            self.PercentFees = {'buy': self.ExBuy.Markets[symbol]['taker'], 'sell': self.ExSell.Markets[symbol]['taker']}
            self.FlatFees = {}

            if type(self.ExBuy.Ex.fees['funding']['withdraw'][self.Base]) == str and self.ExBuy.Ex.fees['funding']['withdraw'][self.Base][-1] == '%':
                self.PercentFees['buy'] += float(self.ExBuy.Ex.fees['funding']['withdraw'][self.Base][0:-1])/100.0
                self.FlatFees['buy'] = 0
            else:
                self.FlatFees['buy'] = self.ExBuy.Ex.fees['funding']['withdraw'][self.Base]

            if type(self.ExSell.Ex.fees['funding']['withdraw'][self.Quote]) == str and self.ExSell.Ex.fees['funding']['withdraw'][self.Quote][-1] == '%':
                self.PercentFees['sell'] += float(self.ExSell.Ex.fees['funding']['withdraw'][self.Quote][0:-1]) / 100.0
                self.FlatFees['sell'] = 0
            else:
                self.FlatFees['sell'] = self.ExSell.Ex.fees['funding']['withdraw'][self.Quote]

        self.Margin = self.ExSell.bid(symbol)/self.ExBuy.ask(symbol)

        if self.min_trade() < self.max_trade():

            try:
                delay = max(int(self.ExBuy.Ex.rateLimit / 1000), int(self.ExSell.Ex.rateLimit / 1000))
                self.BuyAddress = self.ExBuy.Ex.fetch_deposit_address(botutils.quote(self.Symbol))
                self.SellAddress = self.ExSell.Ex.fetch_deposit_address(botutils.base(self.Symbol))
                time.sleep(delay)
                ex1.add_pair(self)
                ex2.add_pair(self)
            except:
                self.ExBuy = None
                self.ExSell = None

    def min_trade(self, flatfee=0, percentfee=0, sigma=bookbuffer, error=0.0001000000001):

        sellmax = self.ExSell.max_order_size(self.Symbol, 'sell')
        buymax = self.ExBuy.max_order_size(self.Symbol, 'buy', converted=True)
        sellmaxadj = min(sellmax, self.ExSell.estimate_sell_cost(self.Symbol, buymax))
        buymaxadj = self.ExBuy.market_buy(self.Symbol, min(buymax, self.ExBuy.estimate_buy_cost(self.Symbol, sellmax)))
        mcount = min(sellmaxadj, buymaxadj)
        sbook = self.ExSell.OrderBooks[self.Symbol]
        bbook = self.ExBuy.OrderBooks[self.Symbol]
        scount = 0
        bcount = 0
        ai = sigma
        bi = sigma
        if sigma >= len(sbook['bids']) or sigma >= len(bbook['asks']):
            return float('inf')

        sprice = sbook['bids'][ai][0]
        bprice = bbook['asks'][bi][0]

        if self.FlatFees['sell'] == 0 and self.FlatFees['buy'] == 0 and sprice > bprice:
            return 0
        if self.Margin <= 1:
            return float('inf')

        while min(scount, bcount) < mcount and ai < len(sbook['bids']) and bi < len(bbook['asks']):

            lcount = min(scount, bcount)
            if scount+self.FlatFees['sell']/self.ExSell.estimate_sell_price(self.Symbol, scount, sigma=sigma) < bcount+self.FlatFees['sell']:
                scount += sbook['bids'][ai][1]
                sprice = sbook['bids'][ai][0] * (1 - self.PercentFees['sell'])
                ai += 1
            else:
                bcount += bbook['asks'][bi][1]
                bprice = bbook['asks'][bi][0] * (1 + self.PercentFees['buy'])
                bi += 1
            if min(scount, bcount) > mcount:
                return float('inf')

            rmin = self.roi(min(scount, bcount), sellbuy='sell', flatfee=flatfee, percentfee=percentfee)
            rlast = self.roi(lcount, sellbuy='sell', flatfee=flatfee, percentfee=percentfee)

            if rmin >= 0:
                if rmin == 0:
                    return min(scount, bcount)
                #todo: figure out why linear interpolation isn't working; maybe splines?
                return lcount - rlast/(rmin-rlast)*(min(scount, bcount)-lcount)

        return float('inf')


    def max_trade(self, percentfee=0, sigma=bookbuffer):

        sellmax = self.ExSell.max_order_size(self.Symbol, 'sell')
        buymax = self.ExBuy.max_order_size(self.Symbol, 'buy', converted=True)
        sellmaxadj = min(sellmax, self.ExSell.estimate_sell_cost(self.Symbol, buymax))
        buymaxadj = self.ExBuy.market_buy(self.Symbol, min(buymax, self.ExBuy.estimate_buy_cost(self.Symbol, sellmax)))
        mcount = min(sellmaxadj, buymaxadj)
        sbook = self.ExSell.OrderBooks[self.Symbol]
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

        while min(scount, bcount) < mcount and smax > bmax and ai < len(sbook['bids']) and bi < len(bbook['asks']):

            lcount = min(scount, bcount)
            if scount < bcount:
                scount += sbook['bids'][ai][1]
                ai+=1
            else:
                bcount += bbook['asks'][bi][1]
                bi+=1

            smax = self.ExSell.estimate_sell_price_at(self.Symbol, min(scount, bcount)) * (1 - self.PercentFees['sell'] - percentfee)
            bmax = self.ExBuy.estimate_buy_price_at(self.Symbol, self.ExSell.market_sell(self.Symbol, min(scount, bcount))) * (1 + self.PercentFees['buy'])

        return lcount

    def margin(self, amount, sellbuy='buy', flatfee=0, percentfee=0, sigma=bookbuffer):

        return (self.roi(amount, sellbuy, flatfee, percentfee, sigma)+amount)/amount if amount != 0 else 0

    def roi(self, amount, sellbuy='buy', flatfee=0, percentfee=0, sigma=bookbuffer):

        if sellbuy == 'sell':

            amt = amount * (1-percentfee) - flatfee

            if amt > self.ExSell.max_order_size(self.Symbol, 'sell'):
                print('above max')
                return -float('inf')

            sold = (self.ExSell.market_sell(self.Symbol, amt - self.PercentFees['sell']*abs(amt)) if amt > 0 else amt) - self.FlatFees['sell']
            bought = (self.ExBuy.market_buy(self.Symbol, sold - self.PercentFees['buy'] * abs(sold)) if amt > 0 else sold) - self.FlatFees['buy']
            return bought - amount

        amt = amount * (1 - percentfee) - flatfee

        if amt > self.ExBuy.max_order_size(self.Symbol, 'buy'):
            print('above max')
            return -float('inf')

        first = ( self.ExBuy.market_buy(self.Symbol, amt) if amt > 0 else amt ) - self.PercentFees['buy']*abs(amt) - self.FlatFees['buy']
        second = ( self.ExSell.market_sell(self.Symbol, first) if amt > 0 else first ) - self.PercentFees['sell']*abs(first) - self.FlatFees['sell']

        return second - amount

    def generate_tx_chain(self, exfrom, cfrom, txlast=None):

        if txlast is not None:
            cf = txlast.SummaryInfo['cto']
            ef = txlast.SummaryInfo['eto']

        else:
            cf = cfrom
            ef = exfrom

        if cf == self.Base:

            if ef == self.ExSell:
                # trade/transfer/trade
                pass
            else:
                # transfer to ex-sell, trade/transfer/trade
                pass

        elif cf == self.Quote:

            if ef == self.ExBuy:
                # trade/transfer/trade
                pass
            elif ef == self.ExSell:
                # transfer to ex-buy, trade/transfer/trade
                pass
        else:
            # todo: pathfinding algorithm for <CF/EF> to <CBase/ESell> or <CQuote/EBuy>, find cheapest way to move funds
            pass

    def __str__(self):
        return 'sell: '+self.ExSell.Ex.name+', buy:'+self.ExBuy.Ex.name+', via '+self.Symbol+' | '+'%.3f' % (100*self.Margin-100)+'% | min: '+"%.5f" % self.min_trade()+' | max: '+'%.5f'%self.max_trade()+' | $'+"%.2f" % botutils.convert_to_USD(self.max_trade(), self.Base)+' -> $'+"%.2f" % botutils.convert_to_USD(self.max_trade()+self.roi(self.max_trade(), sellbuy='sell'), self.Base)