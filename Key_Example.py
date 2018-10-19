import botconfig

#dict of dicts with ccxt-standard 3-letter currency id as the key, and dict with name of coin, public address, and private address
_all_coins = {

    'BTC':{'name':'bitcoin','public':'pubkey','private':'privkey'}}


_all_exchange_keys = {'exchangename':{'key':'apikeypublic','secret':'apikeyprivate'}}

_active_exchanges = ['exchangename']

_active_coins = ['BTC']

_infura_url = "used for infura api calls"

_infura_api_keys = {'public':'pubkey', 'private':'privkey'}

_onchain_key = "onchain_api_key"

_email = "your_email for site logins"


def get_keys(coins=botconfig.active_coins):

    return {coin: _all_coins[coin] for coin in coins}


def get_exchanges(exchanges=botconfig.active_exchanges):

    return {exchange: _all_exchange_keys[exchange] for exchange in exchanges}


def get_email():

    return _email


def get_exchange_password(exchange):
    #fill this out with your passwords
    return


def get_infura_keys():

    return _infura_api_keys


def get_infura_url():

    return _infura_url


def get_onchain_key():

    return _onchain_key
