import requests
import web3
import cryptos
from keys import *

TESTNET = True

cointable = {
    'ETH':'ethereum',
    'BTC':'bitcoin',
    'BCH':'bitcoincash',
    'LTC':'litecoin',
    'DASH':'dash',
}

w3 = web3.Web3(web3.HTTPProvider(infuraurl))

def balance(currency, address):

    if currency in cointable:
        header = {'Accept': 'application/json'}

        try:
            r = requests.get('https://onchain.io/api/address/balance/'+cointable[currency]+'/'+address,
                     params={},
                     headers=header)
            json = r.json()
            # print(json)

            if len(json) > 0:
                return json
            return {}

        except Exception as e:
            print(e)
            return {}

    return {}

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
    tx = coin.preparesignedtx(secret,addressto,amount,fee=fee,change_addr=addressfrom)
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


if __name__ == "__main__":

    addr = "0x1cC3e192d51DeFF9796590c4C33D715f9253d249"
    curr = "ETH"
    print (balance(curr, addr))


