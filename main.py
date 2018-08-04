import ccxt
import csv
import json
import time
import ExchangeWrapper
import CurrencyWrapper
import botconfig
import os
import sys
import MarketRecord
import random

Exchanges = {}
Currencies = {}
Symbols = []
pairedSymbols = []
marketSymbols = {}
pairTable = {}
ExchangeFees = {}
ArbList = {}
QueuedOrders = []
PendingOrders = []
TotalFunds = 0
TotalFundsUSD = 0
TotalAvailable = 0
TotalAvailableUSD = 0

def style(s, style):
    return style + s + '\033[0m'


def green(s):
    return style(s, '\033[92m')


def blue(s):
    return style(s, '\033[94m')


def yellow(s):
    return style(s, '\033[93m')


def red(s):
    return style(s, '\033[91m')


def pink(s):
    return style(s, '\033[95m')


def bold(s):
    return style(s, '\033[1m')


def underline(s):
    return style(s, '\033[4m')


def dump(*args):
    print(' '.join([str(arg) for arg in args]))


def print_exchanges():
    dump('Supported exchanges:', ', '.join(ccxt.exchanges))


def print_usage():
    dump("Usage: python " + sys.argv[0], green('id1'), yellow('id2'), blue('id3'), '...')


def print_ticker(exchange, symbol):
    ticker = exchange.fetch_ticker(symbol.upper())
    print(ticker)
    dump(
        green(exchange.id),
        yellow(symbol),
        'ticker',
        ticker['datetime'],
        'high: ' + str(ticker['high']),
        'low: ' + str(ticker['low']),
        'bid: ' + str(ticker['bid']),
        'ask: ' + str(ticker['ask']),
        'volume: ' + str(ticker['quoteVolume']))


def load_exchanges():

    proxies = [
        '',  # no proxy by default
        'https://crossorigin.me/',
        'https://cors-anywhere.herokuapp.com/',
    ]

    nexs = 0
    with open('apikeys.csv', 'r') as exfile:
        exreader = csv.DictReader(exfile)
        for row in exreader:

            nexs += 1
            exchange = getattr(ccxt, row['Exchange'])()

            try:
                # load all markets from the exchange
                markets = exchange.load_markets()

            # save it in a dictionary under its id for future use
                Exchanges[row['Exchange']] = exchange
                exchange.apiKey = row['Key']
                exchange.secret = row['Secret']
                if exchange.id == 'coinbasepro':
                    exchange.password = botconfig.coinbasepassword
                # instantiate the exchange by id
                dump(green(row['Exchange']), 'loaded', green(str(len(exchange.symbols))), 'markets')

            except Exception as e:
                print(e)
                pass





    dump(green('Loaded ' + str(len(Exchanges)) + " of " + str(nexs) + ' exchanges.'))


def load_currencies():
    with open('cryptokeys.csv', 'r') as cfile:
        coinreader = csv.DictReader(cfile)
        for row in coinreader:
            Currencies[row['COIN']] = CurrencyWrapper.Currency(row['COIN'], row['ADDRESS'], row['PRIVKEY'])
    for c1 in [*Currencies]:
        # print(c1)
        for c2 in [*Currencies]:
            if Currencies[c1].Name != Currencies[c2].Name:
                Symbols.append(Currencies[c1].Name+"/"+Currencies[c2].Name)
    # print("Available Markets:")
    #for s in Symbols:
        # print(s)
    for id in [*Exchanges]:
        balancesheet = Exchanges[id].fetch_balance()
        for currency in [*Currencies]:
            Currencies[currency].add_exchange(Exchanges[id], balancesheet)

    for c in [*Currencies]:
        Currencies[c].check_balance()



def getArbitrageParis():

    ids = [*Exchanges]
    for id in ids:
        marketSymbols[id] = []
    allSymbols = [symbol for id in ids for symbol in Exchanges[id].symbols]

    # get all unique symbols
    uniqueSymbols = list(set(allSymbols))

    # filter out symbols that are not present on at least two exchanges
    arbitrableSymbols = sorted([symbol for symbol in uniqueSymbols if allSymbols.count(symbol) > 1 and symbol in Symbols])

    for symbol in arbitrableSymbols:
        pairedSymbols.append(symbol)
        for id in ids:
            if symbol in Exchanges[id].symbols:
                marketSymbols[id].append(symbol)

    # print a table of arbitrable symbols
    #table = []
    #dump(green(' symbol          | ' + ''.join([' {:<15} | '.format(id) for id in ids])))
    #dump(green(''.join(['-----------------+-' for x in range(0, len(ids) + 1)])))

    #for symbol in arbitrableSymbols:
        # string = ' {:<15} | '.format(symbol)
        # row = {}
        # for id in ids:
        #     # if a symbol is present on a exchange print that exchange's id in the row
        #     string += ' {:<15} | '.format(id if symbol in Exchanges[id].symbols else '')
        # dump(string)


def get_prices():

    dump(green("Fetching market data..."))

    for symbol in pairedSymbols:
        pairTable[symbol] = MarketRecord.MarketRecord(symbol)
        ArbList[symbol] = MarketRecord.ArbitrageList(symbol)

    delay = 0
    maxLength = 0
    for id in [*marketSymbols]:
        dump(yellow("loading..."))
        rlm = int(Exchanges[id].rateLimit/1000)
        ls = len(marketSymbols[id])
        if rlm > delay:
            delay = rlm
        if ls > maxLength:
            maxLength = ls

    try:
        for i in range(0,maxLength):
            time.sleep(delay)
            for id in [*marketSymbols]:
                if i >= len(marketSymbols[id]):
                    continue
                else:
                    exchange = Exchanges[id]
                    symbol = marketSymbols[id][i]
                    try:
                        orderbook = exchange.fetch_order_book(symbol)
                        pairTable[symbol].add_order(orderbook, exchange)
                        ArbList[symbol].add_order(orderbook, exchange, symbol)

                    except ccxt.DDoSProtection as e:
                        print(type(e).__name__, e.args, 'DDoS Protection (ignoring)')
                        pass
                    except ccxt.RequestTimeout as e:
                        print(type(e).__name__, e.args, 'Request Timeout (ignoring)')
                        pass
                    except ccxt.ExchangeNotAvailable as e:
                        print(type(e).__name__, e.args,
                              'Exchange Not Available due to downtime or maintenance (ignoring)')
                        pass
                    except ccxt.AuthenticationError as e:
                        print(type(e).__name__, e.args, 'Authentication Error (missing API keys, ignoring)')
                        pass
                    except Exception as e:
                        #print("Exception:", e.args, exchange, symbol, str(symbol in exchange.symbols))
                        pass

    except Exception as e:

        print(type(e).__name__, e.args, str(e))
        print_usage()

    for symbol in [*ArbList]:
        ArbList[symbol].clean_lists()


def get_balances():


    #check for completed transactions
    #for each exchange and wallet:
    #loop through wallets and sum up usd value of available and total funds
    # *reminder* this includes funds on exchanges that can be withdrawed to other deposit addresses
    #create array of percentages for each currency's share of total available funds
    #update file entries for orders with exact prices after fees, profit, etc

    pass


def select_orders():

    #get balance of all accounts for max
    #get max withdraw of different markets
    #get sorted list of profitable pairs
    #while ask and bid values are less than 80% max balance:
    #   add most profitable bids and asks to queues
    #   make sure queues are balanced 50/50
    #   add order values to counters
    #combine all orders into 1 limit order per exchange

    pass


def allocate_funds():

    #use weight arrays to transfer funds from wallets to exchanges
    #remember that withdraw prices are already included into prices for pairsgg
    #prioritize moving funds on exchanges first, then funds in wallets
    #check for completed orders on exchanges and move funds from ask exchangtes to bid exchanges
    #withdraw all remaining funds on markets

    pass


def place_orders():

    #use trade atomic to place limit orders for queued trades
    #pop filled queued trades and add to pending list
    #figure out a way to block ask/transfer/bid transactions?
    #write placed orders to file
    pass


def trade_atomic(exchange, symbol, price, volume):
    markets = exchange.load_markets(reload=True)
    ordeerbook = exchange.fetch_order_book()

#todo: add interactive front end
#todo: add visualization functions for market depth, arb pair prices, available funds vs total funds, profit
#todo: add functionality to toggle trading


def setup():
    load_exchanges()
    load_currencies()

def main():

    setup()
    getArbitrageParis()
    get_prices()
    print("Arbitrage Pairs:")
    for a in [*ArbList]:
        ArbList[a].print_bids()


    # for symbol in [*pairTable]:
    #     bid = pairTable[symbol].bid_price()
    #     ask = pairTable[symbol].ask_price()
    #
    #     if(bid > ask):
    #         bidVolume = pairTable[symbol].bid()['bids'][0][1]
    #         askVolume = pairTable[symbol].ask()['asks'][0][1]
    #         bidex = pairTable[symbol].bid_exchange().id
    #         askex = pairTable[symbol].ask_exchange().id
    #         print(symbol + " " + askex + "->" + bidex + " - " + "bid: " + str(bidVolume) + " @" + str(bid) + ", ask: " + str(askVolume) + " @" + str(ask) + ", margin: " + str(100*(bid-ask)/ask) + "%")


if __name__ == "__main__":
    main()


# def arbitrage(cycle_num=5, cycle_time=240):
#     #Create Triangular Arbitrage Function
#     print("Arbitrage Function Running")
#     fee_percentage = 0.001          #divided by 100
#     coins = ['BTC', 'LTC', 'ETH']   #Coins to Arbitrage
#     #Create Functionality for Binance
#     for exch in ccxt.exchanges:    #initialize Exchange
#         exchange1 = getattr (ccxt, exch) ()
#         symbols = exchange1.symbols
#         if symbols is None:
#             print("Skipping Exchange ", exch)
#             print("\n-----------------\nNext Exchange\n-----------------")
#         elif len(symbols)<15:
#             print("\n-----------------\nNeed more Pairs (Next Exchange)\n-----------------")
#         else:
#             print(exchange1)
#
#             exchange1_info = dir(exchange1)
#             print("------------Exchange: ", exchange1.id)
#             #pprint(exchange1_info)
#             print(exchange1.symbols)    #List all currencies
#             time.sleep(5)
#             #Find Currencies Trading Pairs to Trade
#             pairs = []
#             for sym in symbols:
#                 for symbol in coins:
#                     if symbol in sym:
#                         pairs.append(sym)
#             print(pairs)
#             #From Coin 1 to Coin 2 - ETH/BTC - Bid
#             #From Coin 2 to Coin 3 - ETH/LTC - Ask
#             #From Coin 3 to Coin 1 - BTC/LTC - Bid
#             arb_list = ['ETH/BTC'] #, 'ETH/LTC', 'BTC/LTC']
#             #Find 'closed loop' of currency rate pairs
#             j=0
#             while 1:
#                 if j == 1:
#                             final = arb_list[0][-3:]  + '/' + str(arb_list[1][-3:])
#                             print(final)
#                             #if final in symbols:
#                             arb_list.append(final)
#                             break
#                 for sym in symbols:
#                     if sym in arb_list:
#                         pass
#                     else:
#                         if j % 2 == 0:
#                             if arb_list[j][0:3] == sym[0:3]:
#                                 if arb_list[j] == sym:
#                                     pass
#                                 else:
#                                     arb_list.append(sym)
#                                     print(arb_list)
#                                     j+=1
#                                     break
#                         if j % 2 == 1:
#                             if arb_list[j][-3:] == sym[-3:]:
#                                 if arb_list[j] == sym:
#                                     pass
#                                 else:
#                                     arb_list.append(sym)
#                                     print(arb_list)
#                                     j+=1
#                                     break
#
#                 #time.sleep(.5)
#             print("List of Arbitrage Symbols:", arb_list)
#             #time.sleep(3)
#         #Determine Rates for our 3 currency pairs - order book
#             list_exch_rate_list = []
#         #Create Visualization of Currency Exchange Rate Value - Over Time
#             #Determine Cycle number (when data is taken) and time when taken
#             for k in range(0,cycle_num):
#                 i=0
#                 exch_rate_list = []
#                 print("Cycle Number: ", k)
#                 for sym in arb_list:
#                     print(sym)
#                     if sym in symbols:
#                         depth = exchange1.fetch_order_book(symbol=sym)
#                         #pprint(depth)
#                         if i % 2 == 0:
#                             exch_rate_list.append(depth['bids'][0][0])
#                         else:
#                             exch_rate_list.append(depth['asks'][0][0])
#                         i+=1
#                     else:
#                         exch_rate_list.append(0)
#                 #exch_rate_list.append(((rateB[-1]-rateA[-1])/rateA[-1])*100)  #Expected Profit
#                 exch_rate_list.append(time.time())      #change to Human Readable time
#                 print(exch_rate_list)
#                 #Compare to determine if Arbitrage opp exists
#                 if exch_rate_list[0]<exch_rate_list[1]/exch_rate_list[2]:
#                     print("Arbitrage Possibility")
#                 else:
#                     print("No Arbitrage Possibility")
#                 #Format data (list) into List format (list of lists)
#                 list_exch_rate_list.append(exch_rate_list)
#                 time.sleep(cycle_time)
#             print(list_exch_rate_list)
#             #Create list from Lists for matplotlib format
#             rateA = []      #Original Exchange Rate
#             rateB = []      #Calculated/Arbitrage Exchange Rate
#             rateB_fee = []  #Include Transaction Fee
#             price1 = []     #List for Price of Token (Trade) 1
#             price2 = []     #List for price of Token (Trade) 2
#             time_list = []  #time of data collection
#             #profit = []     #Record % profit
#             for rate in list_exch_rate_list:
#                 rateA.append(rate[0])
#                 rateB.append(rate[1]/rate[2])
#                 rateB_fee.append((rate[1]/rate[2])*(1-fee_percentage)*(1-fee_percentage))
#                 price1.append(rate[1])
#                 price2.append(rate[2])
#                 #profit.append((rateB[-1]-rateA[-1])/rateA[-1])
#                 time_list.append(rate[3])
#             print("Rate A: {} \n Rate B: {} \n Rate C: {} \n".format(rateA, rateB, rateB_fee))
#             #Visualize with Matplotlib
#             #use matplotlib to plot data
#             #from https://matplotlib.org/api/_as_gen/matplotlib.pyplot.plot.html#matplotlib.pyplot.plot
#         #Extended 3 axis functionality - https://matplotlib.org/gallery/ticks_and_spines/multiple_yaxis_with_spines.html#sphx-glr-gallery-ticks-and-spines-multiple-yaxis-with-spines-py
#             #fig, ax = plt.subplots()
#             fig, host = plt.subplots()
#             fig.subplots_adjust(right=0.75)
#
#             par1 = host.twinx()
#             par2 = host.twinx()
#             par2.spines["right"].set_position(("axes", 1.2))
#             make_patch_spines_invisible(par2)
#             par2.spines["right"].set_visible(True)
#             #Graph Rate & Calculated Rate on Left Hand Side
#             p1, = host.plot(time_list, rateA, "k", label = "{}".format(arb_list[0]))
#             p1, = host.plot(time_list, rateB, "k+", label = "{} / {}".format(arb_list[1], arb_list[2]))
#             #p1, = host.plot(time_list, rateB_fee, 'k+', label = "{} / {} - with Fee".format(arb_list[1], arb_list[2]))
#             #Graph Exchange Rate (Originals)
#             p2, = par1.plot(time_list, price1, "b-", label="Price - {}".format(arb_list[1]))
#             p3, = par2.plot(time_list, price2, "g-", label="Price - {}".format(arb_list[2]))
#             #show our graph - with labels
#
#             host.set_xlabel("Time")
#             host.set_ylabel("Exchange Rate")
#             par1.set_ylabel("Price - {}".format(arb_list[1]))
#             par2.set_ylabel("Price - {}".format(arb_list[2]))
#             host.yaxis.label.set_color(p1.get_color())
#             tkw = dict(size=4, width=1.5)
#             host.tick_params(axis='y', colors=p1.get_color(), **tkw)
#             par1.tick_params(axis='y', colors=p2.get_color(), **tkw)
#             par2.tick_params(axis='y', colors=p3.get_color(), **tkw)
#             host.tick_params(axis='x', **tkw)
#             #ax.set(xlabel='Date', ylabel='Exchange Rate', title='Exchange: {}'.format(exch))
#             lines = [p1, p2, p3]
#             host.legend(lines, [l.get_label() for l in lines])  #show Legend
#             plt.show()
