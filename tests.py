import ccxt
import Exchange
import Pair
import botutils


abook = {
    'bids':[
[2, 1],[2, 1],[2, 1],[2, 1],[2, 1],[2, 1],[2, 1],[2, 1],[2, 1],[2, 1],
[1.5, 1],[1.5, 1],[1.5, 1],[1.5, 1],[1.5, 1],[1.5, 1],[1.5, 1],[1.5, 1],[1.5, 1],[1.5, 1],
[1, 1],[1, 1],[1, 1],[1, 1],[1, 1],[1, 1],[1, 1],[1, 1],[1, 1],[1, 1],
[0.5, 1],[0.5, 1],[0.5, 1],[0.5, 1],[0.5, 1],[0.5, 1],[0.5, 1],[0.5, 1],[0.5, 1],[0.5, 1],],
    'asks':[
[2.5,1],[2.5,1],[2.5,1],[2.5,1],[2.5,1],[2.5,1],[2.5,1],[2.5,1],[2.5,1],[2.5,1],
[3.0,1],[3.0,1],[3.0,1],[3.0,1],[3.0,1],[3.0,1],[3.0,1],[3.0,1],[3.0,1],[3.0,1],
[3.5,1],[3.5,1],[3.5,1],[3.5,1],[3.5,1],[3.5,1],[3.5,1],[3.5,1],[3.5,1],[3.5,1],]
}

bbook = {
    'bids':[
[3, 1],[3, 1],[3, 1],[3, 1],[3, 1],[3, 1],[3, 1],[3, 1],[3, 1],[3, 1],
[2.5, 1],[2.5, 1],[2.5, 1],[2.5, 1],[2.5, 1],[2.5, 1],[2.5, 1],[2.5, 1],[2.5, 1],[2.5, 1],
[2, 1],[2, 1],[2, 1],[2, 1],[2, 1],[2, 1],[2, 1],[2, 1],[2, 1],[2, 1],
[1.5, 1],[1.5, 1],[1.5, 1],[1.5, 1],[1.5, 1],[1.5, 1],[1.5, 1],[1.5, 1],[1.5, 1],[1.5, 1],],
    'asks':[
[3.5,2],[3.5,2],[3.5,2],[3.5,2],[3.5,2],[3.5,2],[3.5,2],[3.5,2],[3.5,2],[3.5,2],
[4.0,2],[4.0,2],[4.0,2],[4.0,2],[4.0,2],[4.0,2],[4.0,2],[4.0,2],[4.0,2],[4.0,2],
[4.5,2],[4.5,2],[4.5,2],[4.5,2],[4.5,2],[4.5,2],[4.5,2],[4.5,2],[4.5,2],[4.5,2],]
}

cbook = {
    'bids':[],
    'asks':[]}

dbook = {
    'bids':[
[2, 1],[2, 1],[2, 1],[2, 1],[2, 1],[2, 1],[2, 1],[2, 1],[2, 1],[2, 1],
[1.5, 1],[1.5, 1],[1.5, 1],[1.5, 1],[1.5, 1],[1.5, 1],[1.5, 1],[1.5, 1],[1.5, 1],[1.5, 1],
[1, 1],[1, 1],[1, 1],[1, 1],[1, 1],[1, 1],[1, 1],[1, 1],[1, 1],[1, 1],
[0.5, 1],[0.5, 1],[0.5, 1],[0.5, 1],[0.5, 1],[0.5, 1],[0.5, 1],[0.5, 1],[0.5, 1],[0.5, 1],],
    'asks':[
[2.5,1],[2.5,1],[2.5,1],[2.5,1],[2.5,1],[2.5,1],[2.5,1],[2.5,1],[2.5,1],[2.5,1],
[3.0,1],[3.0,1],[3.0,1],[3.0,1],[3.0,1],[3.0,1],[3.0,1],[3.0,1],[3.0,1],[3.0,1],
[3.5,1],[3.5,1],[3.5,1],[3.5,1],[3.5,1],[3.5,1],[3.5,1],[3.5,1],[3.5,1],[3.5,1],]
}

ebook = {
    'bids':[
[7, 10],[7, 10],[7, 10],[7, 10],[7, 10],[7, 10],[7, 10],[7, 10],[7, 10],[7, 10],
[6.5, 10],[6.5, 10],[6.5, 10],[6.5, 10],[6.5, 10],[6.5, 10],[6.5, 10],[6.5, 10],[6.5, 10],[6.5, 10],
[6, 10],[6, 10],[6, 10],[6, 10],[6, 10],[6, 10],[6, 10],[6, 10],[6, 10],[6, 10],
[5.5, 10],[5.5, 10],[5.5, 10],[5.5, 10],[5.5, 10],[5.5, 10],[5.5, 10],[5.5, 10],[5.5, 10],[5.5, 10],],
    'asks':[
[8.5,10],[8.5,10],[8.5,10],[8.5,10],[8.5,10],[8.5,10],[8.5,10],[8.5,10],[8.5,10],[8.5,10],
[9.0,10],[9.0,10],[9.0,10],[9.0,10],[9.0,10],[9.0,10],[9.0,10],[9.0,10],[9.0,10],[9.0,10],
[9.5,10],[9.5,10],[9.5,10],[9.5,10],[9.5,10],[9.5,10],[9.5,10],[9.5,10],[9.5,10],[9.5,10],]
}

fbook = {
    'bids':[
[7, 0.1],[7, 0.1],[7, 0.1],[7, 0.1],[7, 0.1],[7, 0.1],[7, 0.1],[7, 0.1],[7, 0.1],[7, 0.1],
[6.5, 0.1],[6.5, 0.1],[6.5, 0.1],[6.5, 0.1],[6.5, 0.1],[6.5, 0.1],[6.5, 0.1],[6.5, 0.1],[6.5, 0.1],[6.5, 0.1],
[6, 0.1],[6, 0.1],[6, 0.1],[6, 0.1],[6, 0.1],[6, 0.1],[6, 0.1],[6, 0.1],[6, 0.1],[6, 0.1],
[5.5, 0.1],[5.5, 0.1],[5.5, 0.1],[5.5, 0.1],[5.5, 0.1],[5.5, 0.1],[5.5, 0.1],[5.5, 0.1],[5.5, 0.1],[5.5, 0.1],],
    'asks':[
[8.5,0.1],[8.5,0.1],[8.5,0.1],[8.5,0.1],[8.5,0.1],[8.5,0.1],[8.5,0.1],[8.5,0.1],[8.5,0.1],[8.5,0.1],
[9.0,0.1],[9.0,0.1],[9.0,0.1],[9.0,0.1],[9.0,0.1],[9.0,0.1],[9.0,0.1],[9.0,0.1],[9.0,0.1],[9.0,0.1],
[9.5,0.1],[9.5,0.1],[9.5,0.1],[9.5,0.1],[9.5,0.1],[9.5,0.1],[9.5,0.1],[9.5,0.1],[9.5,0.1],[9.5,0.1],]
}


def test1():
    bin = Exchange.Exchange(ccxt.binance())
    bin.add_book(bin.Ex.fetch_order_book('BCD/BTC'), 'BCD/BTC')
    hit = Exchange.Exchange(ccxt.bitz())
    hit.add_book(hit.Ex.fetch_order_book('BCD/BTC'), 'BCD/BTC')
    pair = Pair.Pair(hit, bin, 'BCD/BTC')
    print(pair.max_trade())
    print(pair.min_trade())
    print(pair.margin())

def test2():
    symbol = 'ETH/BTC'
    t1 = Exchange.Exchange(ccxt.binance())
    t1.add_book(abook, symbol)
    t2 = Exchange.Exchange(ccxt.bitz())
    t2.add_book(ebook, 'ETH/BTC')
    pair = Pair.Pair(t1, t2, 'ETH/BTC')
    print(pair.max_trade())
    print(pair.min_trade())
    print(pair.Margin)
    print(pair.FlatFees)
    print(pair.PercentFees)


def test3():
    symbol = 'ETH/BTC'
    t1 = Exchange.Exchange(ccxt.binance())
    t1.add_book(abook, symbol)
    t2 = Exchange.Exchange(ccxt.bitz())
    t2.add_book(fbook, 'ETH/BTC')
    pair = Pair.Pair(t1, t2, 'ETH/BTC')
    print(pair.max_trade())
    print(pair.min_trade())
    print(pair.Margin)
    print(pair.FlatFees)
    print(pair.PercentFees)

def test4():
    symbol = 'BCD/BTC'
    t1 = Exchange.Exchange(ccxt.binance())
    t1.add_book(abook, symbol)
    t2 = Exchange.Exchange(ccxt.bitz())
    t2.add_book(cbook, 'BCD/BTC')
    pair = Pair.Pair(t1, t2, 'BCD/BTC')
    print(pair.max_trade())
    print(pair.min_trade())
    print(pair.Margin)
    print(pair.FlatFees)
    print(pair.PercentFees)

def test5():
    symbol = 'ETH/BTC'
    t1 = Exchange.Exchange(ccxt.binance())
    t1.add_book(abook, symbol)
    t2 = Exchange.Exchange(ccxt.hitbtc())
    t2.add_book(bbook, 'ETH/BTC')
    pair = Pair.Pair(t1, t2, 'ETH/BTC')
    print('~~~~~',pair.max_trade())
    print('~~~~',pair.min_trade())
    print('~~~',pair.Margin)
    print('~~',pair.margin(pair.max_trade()))
    print('~',pair.margin(pair.min_trade()))
    print('$',"%.2f" % botutils.convert_to_USD(pair.max_trade(), 'ETH'),' -> $',"%.2f" % botutils.convert_to_USD(pair.max_trade()+pair.roi(pair.max_trade()), 'ETH'))
    print('roilim:', (pair.roi(pair.max_trade())-pair.roi(pair.max_trade()*0.999))*1000)


def test6():
    symbol = 'ETH/BTC'
    t1 = Exchange.Exchange(ccxt.binance())
    t1.add_book(abook, symbol)
    t2 = Exchange.Exchange(ccxt.hitbtc())
    t2.add_book(bbook, 'ETH/BTC')
    pair = Pair.Pair(t1, t2, 'ETH/BTC')
    for i in range(int(10*pair.min_trade()), int(10*pair.max_trade())):
        print(pair.roi(i/10.0))


def test7():
    symbol = 'ETH/BTC'
    t1 = Exchange.Exchange(ccxt.binance())
    t1.add_book(abook, symbol)
    t2 = Exchange.Exchange(ccxt.hitbtc())
    t2.add_book(abook, 'ETH/BTC')
    pair = Pair.Pair(t1, t2, 'ETH/BTC')
    print(pair.max_trade())
    print(pair.min_trade())
    print(pair.Margin)
    print(pair.margin(pair.max_trade()))
    print(pair.margin(pair.min_trade()))
    print('$', "%.2f" % botutils.convert_to_USD(pair.max_trade(), 'ETH'), ' -> $',
          "%.2f" % botutils.convert_to_USD(pair.max_trade() + pair.roi(pair.max_trade()), 'ETH'))

def test8():
    symbol = 'ETH/USDT'
    t1 = Exchange.Exchange(ccxt.exmo())
    t1.add_book(t1.Ex.fetch_order_book(symbol), symbol)
    t2 = Exchange.Exchange(ccxt.ethfinex())
    t2.add_book(t2.Ex.fetch_order_book(symbol), symbol)
    pair = Pair.Pair(t1, t2, 'ETH/USDT')


def main():
    test8()

if __name__ == "__main__":
    main()
