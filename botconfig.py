
active_exchanges = ['binance','hitbtc','coinbasepro','ethfinex','bitbay','bittrex','exmo','fcoin','bigone','kucoin','coinex','bitz','zb','cryptopia','tidex','liqui','livecoin','bithumb','bibox']
#['binance','hitbtc','kraken','coinbasepro','ethfinex','bitbay','bittrex','exmo','fcoin','bigone','kucoin','coinex','bitz','yobit']
#['binance','hitbtc','coinbasepro','ethfinex','bitbay','bittrex','exmo','fcoin','bigone','kucoin','coinex', 'bitz']
#['coinbasepro','ethfinex','bitbay','exmo','fcoin','bigone','coinex']
#['coinbasepro','bitbay','exmo','bigone']

active_coins = ['BTC','BCH','ETH','LTC','DASH']

blacklisted_coins = ['BOX']

withdraw_limits = {'binance':{'BTC':100},
                   'hitbtc':float('inf'),
                   'kraken':{'USD':200000},
                   'kucoin':float('inf'),
                   'bittrex':{'BTC':100},
                   'yobit':float('inf'),
                   'bigone':float('inf'),
                   'exmo':float('inf'),
                   'ethfinex':float('inf'),
                    'bitbay':float('inf'),
                    'bitz':{'BTC':20},
                    'fcoin':{'BTC':150,'ETH':2500,'BCH':1200,'LTC':8000,'USDT':500000,'FT':1500000,'ZIP':200000000,'ETC':120000,'BTM':800000,'ZIL':3000000,'OMG':200000,'ICX':8000000,'ZRX':500000,'BNB':120000,'GTC':150000000,'AE':1000000},
                    'coinbasepro':{'USD':10000},
                    'coinex':float('inf'),
                    'bibox':{'BTC':20},
                    'zb':float('inf'),
                    'bithumb':{'BTC':0},
                    'cryptopia':{'USD':20000},
                    'liqui':{'USDT':50000,'USD':48000},
                    'tidex':float('inf'),
                    'livecoin':float('inf')
                   }

max_single_withdraw = {'kucoin':{'BTC':50}}

#skips this many orders in the book to offset trades made after orders have been fetched and before calculations can be made
#TODO: replace this with estimated currency amounts based off of individual exchange/currency trade volume data
#TODO: improve the above todo with a cyclical curve to represent peak trading hours each day
order_book_trade_buffer = 0

require_fees = False

default_fee_percent = 0.00

max_margin = 100
min_margin = 1