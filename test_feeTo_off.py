import asyncio
import configparser
import os
import time
import web3
import ethereum


FEED_PRIVATE_KEY = bytes.fromhex('d95d6db65f3e2223703c5d8e205d98e3e6b470f067b0f94f6c6bf73d4301ce48')

CHAIN_ID = 41
LOCALNET_NODE = 'http://127.0.0.1:7070'
DEVNET_NODE = 'http://88.99.87.58:7070'
TESTNET_NODE = 'http://95.217.17.248:7070'


class Wallet:
    def __init__(self, private_key, connection):
        self.private_key = private_key
        self.address = ethereum.utils.checksum_encode(ethereum.utils.privtoaddr(self.private_key))
        self.connection = connection
        self.nonce = self.connection.eth.getTransactionCount(self.address)

    def send(self, to, amount):
        transaction = {
            'from': self.address,
            'to': to,
            'value': amount,
            'gas': 4000000,
            'gasPrice': 1,
            'nonce': self.nonce,
            'chainId': CHAIN_ID
        }
        signed = web3.eth.Account.signTransaction(transaction, self.private_key)
        txid = self.connection.eth.sendRawTransaction(signed.rawTransaction)
        self.nonce += 1
        return txid

    def tx_info(self, txid):
        return self.connection.eth.getTransactionReceipt(txid)

    def update_nonce(self):
        self.nonce = self.connection.eth.getTransactionCount(self.address)

    def deploy_contract(self, bytecode, abi):
        contract = self.connection.eth.contract(bytecode=bytecode,  abi=abi)
        tx = contract.constructor().buildTransaction({'from': self.address, "nonce": self.nonce, "gasPrice": 1})
        signed = web3.eth.Account.signTransaction(tx, self.private_key)
        txid = bytes.hex(self.connection.eth.sendRawTransaction(signed.rawTransaction))
        tx_receipt = self.connection.eth.wait_for_transaction_receipt(txid)
        return tx_receipt.contractAddress

    def mint(self, contract_address, abi, address, amount):
        contract = self.connection.eth.contract(address=contract_address, abi=abi)
        tx = contract.functions.mint(address, amount).buildTransaction({'from': self.address, "nonce": self.nonce, "gasPrice": 1, 'gas': 100000000000})
        signed = web3.eth.Account.signTransaction(tx, self.private_key)
        txid = bytes.hex(self.connection.eth.sendRawTransaction(signed.rawTransaction))
        tx_receipt = self.connection.eth.wait_for_transaction_receipt(txid)
        return tx_receipt

    def transfer(self, contract_address, abi, address, amount):
        contract = self.connection.eth.contract(address=contract_address, abi=abi)
        tx = contract.functions.transfer(address, amount).buildTransaction({'from': self.address, "nonce": self.nonce, "gasPrice": 1, 'gas': 100000000000})
        signed = web3.eth.Account.signTransaction(tx, self.private_key)
        txid = bytes.hex(self.connection.eth.sendRawTransaction(signed.rawTransaction))
        tx_receipt = self.connection.eth.wait_for_transaction_receipt(txid)
        return tx_receipt

    def balanceOf(self, contract_address, abi, address):
        contract = self.connection.eth.contract(address=contract_address, abi=abi)
        return contract.functions.balanceOf(address).call()

    def totalSupply(self, contract_address, abi):
        contract = self.connection.eth.contract(address=contract_address, abi=abi)
        return contract.functions.totalSupply().call()

    def call(self, contract_address, abi):
        contract = self.connection.eth.contract(address=contract_address, abi=abi)
        return contract.functions.balanceOf('0x32D2b9bBCf25525b8D7E92CBAB14Ca1a5f347B14').call()
        #return self.connection.eth.call({'value': 0, 'gas': 100000000000, 'to': '0x52C050eFdd9F23b08abAC34558F4F817fd71bFa2', 'data': '0x399542e9000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000400000000000000000000000000000000000000000000000000000000000000002000000000000000000000000000000000000000000000000000000000000004000000000000000000000000000000000000000000000000000000000000000e0000000000000000000000000327b1fb4173308ad6eafc4a73af2a6e61c15a87d0000000000000000000000000000000000000000000000000000000000000040000000000000000000000000000000000000000000000000000000000000002470a082310000000000000000000000006bc32575acb8754886dc283c2c8ac54b1bd93195000000000000000000000000000000000000000000000000000000000000000000000000000000005f7832a4e1cc385af56365588ab621e2dc5866010000000000000000000000000000000000000000000000000000000000000040000000000000000000000000000000000000000000000000000000000000002470a082310000000000000000000000006bc32575acb8754886dc283c2c8ac54b1bd9319500000000000000000000000000000000000000000000000000000000'})
        #return contract.functions.tryBlockAndAggregate(False, [['0x52C050eFdd9F23b08abAC34558F4F817fd71bFa2', '0x0f28c97d'], ['0x52C050eFdd9F23b08abAC34558F4F817fd71bFa2', '0x4d2301cc000000000000000000000000eba87350c12e72d863aef82853eac0aab4c4e86a'], ['0x5F7832A4e1Cc385af56365588ab621e2Dc586601', '0x70a08231000000000000000000000000eba87350c12e72d863aef82853eac0aab4c4e86a']]).call()

    def createPair(self, contract_address, abi, tokenA, tokenB):
        contract = self.connection.eth.contract(address=contract_address, abi=abi)
        tx = contract.functions.createPair(tokenA, tokenB).buildTransaction({'from': self.address, "nonce": self.nonce, "gasPrice": 1, 'gas': 100000000000})
        signed = web3.eth.Account.signTransaction(tx, self.private_key)
        txid = bytes.hex(self.connection.eth.sendRawTransaction(signed.rawTransaction))
        tx_receipt = self.connection.eth.wait_for_transaction_receipt(txid)
        return tx_receipt

    def mintPair(self, contract_address, abi, address):
        contract = self.connection.eth.contract(address=contract_address, abi=abi)
        tx = contract.functions.mint(address).buildTransaction({'from': self.address, "nonce": self.nonce, "gasPrice": 1, 'gas': 100000000000})
        signed = web3.eth.Account.signTransaction(tx, self.private_key)
        txid = bytes.hex(self.connection.eth.sendRawTransaction(signed.rawTransaction))
        tx_receipt = self.connection.eth.wait_for_transaction_receipt(txid)
        return tx_receipt

    def swapPair(self, contract_address, abi, amount0Out, amount1Out, to, data):
        contract = self.connection.eth.contract(address=contract_address, abi=abi)
        tx = contract.functions.swap(amount0Out, amount1Out, to, data).buildTransaction({'from': self.address, "nonce": self.nonce, "gasPrice": 1, 'gas': 100000000000})
        signed = web3.eth.Account.signTransaction(tx, self.private_key)
        txid = bytes.hex(self.connection.eth.sendRawTransaction(signed.rawTransaction))
        tx_receipt = self.connection.eth.wait_for_transaction_receipt(txid)
        return tx_receipt

    def burnPair(self, contract_address, abi, to):
        contract = self.connection.eth.contract(address=contract_address, abi=abi)
        tx = contract.functions.burn(to).buildTransaction({'from': self.address, "nonce": self.nonce, "gasPrice": 1, 'gas': 100000000000})
        signed = web3.eth.Account.signTransaction(tx, self.private_key)
        txid = bytes.hex(self.connection.eth.sendRawTransaction(signed.rawTransaction))
        tx_receipt = self.connection.eth.wait_for_transaction_receipt(txid)
        return tx_receipt

    def getPair(self, contract_address, abi, tokenA, tokenB):
        contract = self.connection.eth.contract(address=contract_address, abi=abi)
        return contract.functions.getPair(tokenA, tokenB).call()

    def getReserves(self, contract_address, abi):
        contract = self.connection.eth.contract(address=contract_address, abi=abi)
        return contract.functions.getReserves().call()
    
if __name__ == '__main__':
    with open("LRC20_1.abi", "r") as abifile:
        abiLRC20_1 = abifile.read()
    with open("LRC20_1.wasm", "rb") as wasmfile:
        bytecodeLRC20_1 = bytes.hex(wasmfile.read())

    with open("LRC20_2.abi", "r") as abifile:
        abiLRC20_2 = abifile.read()
    with open("LRC20_2.wasm", "rb") as wasmfile:
        bytecodeLRC20_2 = bytes.hex(wasmfile.read())

    with open("UniswapV2Factory.abi", "r") as abifile:
        abiUniswapV2Factory = abifile.read()
    with open("UniswapV2Factory.wasm", "rb") as wasmfile:
        bytecodeUniswapV2Factory = bytes.hex(wasmfile.read())

    with open("UniswapV2Pair.abi", "r") as abifile:
        abiUniswapV2Pair = abifile.read()
    with open("UniswapV2Pair.wasm", "rb") as wasmfile:
        bytecodeUniswapV2Pair = bytes.hex(wasmfile.read())
    
    node = web3.Web3(web3.Web3.HTTPProvider(LOCALNET_NODE))
    feed_wallet = Wallet(FEED_PRIVATE_KEY, node)
    
    # Init
    addressLRC20_1 = feed_wallet.deploy_contract(bytecodeLRC20_1, abiLRC20_1)
    feed_wallet.update_nonce()
    print("LRC20_1: " + str(addressLRC20_1))

    addressLRC20_2 = feed_wallet.deploy_contract(bytecodeLRC20_2, abiLRC20_2)
    feed_wallet.update_nonce()
    print("LRC20_2: " + str(addressLRC20_2))

    addressUniswapV2Factory = feed_wallet.deploy_contract(bytecodeUniswapV2Factory, abiUniswapV2Factory)
    feed_wallet.update_nonce()
    print("UniswapV2Factory: " + str(addressUniswapV2Factory))

    resultCreatePair = feed_wallet.createPair(addressUniswapV2Factory, abiUniswapV2Factory, addressLRC20_1, addressLRC20_2)
    feed_wallet.update_nonce()
    print("CreatePair: " + str(resultCreatePair))

    addressUniswapV2Pair = feed_wallet.getPair(addressUniswapV2Factory, abiUniswapV2Factory, addressLRC20_1, addressLRC20_2)
    feed_wallet.update_nonce()
    print("UniswapV2Pair: " + str(addressUniswapV2Pair))

    # Test
    token0Amount = 1000000000000000000000
    token1Amount = 1000000000000000000000
    swapAmount = 1000000000000000000
    expectedOutputAmount = 996006981039903216
    expectedLiquidity = 1000000000000000000000
    MINIMUM_LIQUIDITY = 1000

    resultMintLRC20_1 = feed_wallet.mint(addressLRC20_1, abiLRC20_1, addressUniswapV2Pair, token0Amount)
    feed_wallet.update_nonce()
    print("MintLRC20_1: " + str(resultMintLRC20_1))

    resultMintLRC20_2 = feed_wallet.mint(addressLRC20_2, abiLRC20_2, addressUniswapV2Pair, token1Amount)
    feed_wallet.update_nonce()
    print("MintLRC20_2: " + str(resultMintLRC20_2))

    resultMintPair = feed_wallet.mintPair(addressUniswapV2Pair, abiUniswapV2Pair, feed_wallet.address)
    feed_wallet.update_nonce()
    print("ResultMintPair: " + str(resultMintPair))

    resultMintLRC20_2 = feed_wallet.mint(addressLRC20_2, abiLRC20_2, addressUniswapV2Pair, swapAmount)
    feed_wallet.update_nonce()
    print("MintLRC20_2: " + str(resultMintLRC20_2))

    resultSwap = feed_wallet.swapPair(addressUniswapV2Pair, abiUniswapV2Pair, expectedOutputAmount, 0, feed_wallet.address, '0x')
    feed_wallet.update_nonce()
    print("Swap: " + str(resultSwap))

    resultTransferPair = feed_wallet.transfer(addressUniswapV2Pair, abiUniswapV2Pair, addressUniswapV2Pair, expectedLiquidity - MINIMUM_LIQUIDITY)
    feed_wallet.update_nonce()
    print("TransferPair: " + str(resultTransferPair))

    resultBurn = feed_wallet.burnPair(addressUniswapV2Pair, abiUniswapV2Pair, feed_wallet.address)
    feed_wallet.update_nonce()
    print("Burn: " + str(resultBurn))

    # Check
    print(feed_wallet.totalSupply(addressUniswapV2Pair, abiUniswapV2Pair) == MINIMUM_LIQUIDITY)


