import requests
import ccxt
import web3
import cryptos
import coinmarketcap
from keys import *


#TESTNET = True

cointable = {
    'ETH':'ethereum',
    'BTC':'bitcoin',
    'BCH':'bitcoincash',
    'LTC':'litecoin',
    'DASH':'dash',
}

cap = coinmarketcap.Market()
tickerdata = cap.ticker()['data']

iso_currencies = ['KHR', 'MRU', 'SOS', 'TND', 'MVR', 'ARS', 'XCD', 'FKP', 'MAD', 'TZS', 'CLP', 'MMK', 'HKD', 'RON', 'PAB', 'THB', 'HNL', 'BTN', 'EGP', 'SRD', 'SVC', 'SGD', 'NGN', 'XSU', 'KPW', 'KYD', 'COU', 'SHP', 'UYU', 'GIP', 'SLL', 'CZK', 'BOV', 'KZT', 'LBP', 'MDL', 'KES', 'DJF', 'KRW', 'DOP', 'MXV', 'HRK', 'PYG', 'KGS', 'NPR', 'PGK', 'HTG', 'SEK', 'GNF', 'UAH', 'IQD', 'PLN', 'ETB', 'SBD', 'INR', 'CHW', 'TRY', 'BGN', 'GMD', 'BYN', 'CHE', 'GHS', 'TTD', 'AFN', 'MOP', 'MKD', 'NIO', 'XPF', 'AOA', 'MZN', 'TWD', 'LRD', 'UZS', 'BWP', 'BZD', 'MXN', 'VND', 'SCR', 'AWG', 'PKR', 'TMT', 'XAF', 'STN', 'BRL', 'CRC', 'RUB', 'SSP', 'BDT', 'SDG', 'CUP', 'LYD', 'AUD', 'YER', 'IDR', 'LAK', 'USD', 'MGA', 'LSL', 'DZD', 'NZD', 'EUR', 'AMD', 'JPY', 'COP', 'GYD', 'OMR', 'JMD', 'BIF', 'CHF', 'JOD', 'BHD', 'KMF', 'BND', 'FJD', 'LKR', 'BSD', 'SYP', 'VEF', 'TOP', 'SAR', 'WST', 'HUF', 'UYI', 'GTQ', 'ILS', 'ZWL', 'BAM', 'ALL', 'GBP', 'UGX', 'TJS', 'MYR', 'MWK', 'ERN', 'VUV', 'BOB', 'SZL', 'BMD', 'XDR', 'RWF', 'KWD', 'XUA', 'CDF', 'NOK', 'MUR', 'NAD', 'CAD', 'CUC', 'ISK', 'ZAR', 'QAR', 'RSD', 'XOF', 'PEN', 'USN', 'ZMW', 'GEL', 'CNY', 'BBD', 'PHP', 'MNT', 'AED', 'ANG', 'CLF', 'CVE', 'DKK', 'IRR', 'AZN']

#withdraw limits for exchanges. 0 means that withdraw is disabled
withdraw_limits = {'hitbtc':float('inf')}

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


def convert_from_USD(amount, currency, sigma=0):
    for i in [*tickerdata]:
        if tickerdata[i]['symbol'] == currency:
            return (1+sigma)*amount*(1/tickerdata[i]['quotes']['USD']['price'])
    return 0

def convert_to_USD(amount, currency, sigma=0):
    for i in [*tickerdata]:
        if tickerdata[i]['symbol'] == currency:
            return (1-sigma)*amount*(tickerdata[i]['quotes']['USD']['price'])
    return 0


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


w3 = web3.Web3(web3.HTTPProvider(get_infura_url()))

# def balance(currency, address):
#
#     if currency in cointable:
#         header = {'Accept': 'application/json', 'X-API-KEY': get_onchain_key()}
#
#         try:
#             r = requests.get('https://onchain.io/api/address/balance/'+cointable[currency]+'/'+address,
#                      params={},
#                      headers=header)
#             json = r.json()
#             # print(json)
#
#             if len(json) > 0:
#                 return json
#             return {}
#
#         except Exception as e:
#             print(e)
#             return {}
#
#     return {}

def balance(currency, address):


    try:
        assert currency in [*cointable]
        if currency == 'ETH':
            balance = w3.eth.getBalance(address)
            return web3.utils.fromWei(balance)
        else:
            if currency == 'BTC':
                coin = cryptos.Bitcoin()
            if currency == 'LTC':
                coin = cryptos.Litecoin()
            if currency == 'DASH':
               coin = cryptos.Dash()
            if currency == 'BCH':
                coin = cryptos.BitcoinCash()
            balance = coin.history(address)['final_balance']
            return balance

    except Exception as e:
        print(e)
        return 0



def transfer(currency, amount, addressto, addressfrom, secret):

    if currency == 'ETH':
        receipt = send_eth(amount, addressto, addressfrom, secret)
    if currency == 'BTC':
        coin = cryptos.Bitcoin()
    if currency == 'LTC':
        coin = cryptos.Litecoin()
    if currency == 'DASH':
        coin = cryptos.Dash()
    if currency == 'BCH':
        coin = cryptos.BitcoinCash()
    tx = coin.preparesignedtx(secret,addressto,amount,change_addr=addressfrom)
    receipt = cryptos.pushtx(tx)


def send_eth(amount, addressto, addressfrom, secret):

    amt = web3.toWei(amount, 'ether')
    to = w3.toChecksumAddress(addressto)
    frm = w3.toChecksumAddress(addressfrom)
    gasprice = w3.eth.gasPrice
    gas = w3.eth.estimateGas({'to':to, 'from':frm})
    transaction = {
        'to': addressto,
        'value': amt,
        'gas': gas,
        'gasPrice': gasprice,
        'nonce': w3.eth.getTransactionCount(frm),
        'chainId': 1
    }
    signedtxn = w3.eth.account.signTransaction(transaction, private_key=secret)
    w3.eth.sendRawTransaction(signedtxn.rawTtansaction)
    return w3.eth.waitForTransactionReceipt(signedtxn.hash, timeout=1200)

def base(symbol):
    return symbol.split('/')[0]

def quote(symbol):
    return symbol.split('/')[1]

def check_symbol(symbol):

    try:
        b = base(symbol)
        q = quote(symbol)
        return (not b in iso_currencies) and (not q in iso_currencies) and (not b in botconfig.blacklisted_coins) and (not q in botconfig.blacklisted_coins)

    except:
        return False


if __name__ == "__main__":

    addr = "0x1cC3e192d51DeFF9796590c4C33D715f9253d249"
    curr = "ETH"
    print (balance(curr, addr))


