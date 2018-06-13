import time
from flask import render_template, request
from flask_socketio import SocketIO, emit,join_room
from app import  jsonrpc,app,socketio
from app import service
from utils import verify_password

from config import setting


# @app.route('/')
# def index():
#     return render_template('index.html')


# @socketio.on('connect_event')
# def connected_msg(msg):
#     print (msg['data'])
#     # while True:
#     emit('server_response', {'data': msg['data']})
#     # time.sleep(1)
#
# @socketio.on('client_event')
# def client_msg(msg):
#
#     join_room(1)
#     block_height = service.query_block_height_by_txid(msg['data'])
#     emit('server_response', {'data': block_height},room=1)



# @jsonrpc.method("createMultiSigAddress")
# def create_multisig_address(publicKey1,publicKey2,publicKey3):
#     return service.createMultiSigContract(publicKey1,publicKey2,publicKey3)




@jsonrpc.method("constructTx")
def construct_tx(addressFrom,addressTo,value,assetId):
    return service.construct_tx(addressFrom,addressTo,value,assetId)




@jsonrpc.method("sign")
def sign(txData,privtKey):
    return service.sign(txData,privtKey)


# @jsonrpc.method("multiSign")
# def multi_sign(txData,privtKey1,privtKey2,verificationScript):
#     return service.multi_sign(txData,privtKey1,privtKey2,verificationScript)


@jsonrpc.method("sendRawTx")
def send_raw_tx(rawTx):
    return service.send_raw_tx(rawTx)

@jsonrpc.method("getTransaction")
def get_transaction(txid):
    return service.get_transaction(txid)

@jsonrpc.method("getTransactionByAddress")
def get_transaction_by_address(address,asset):
    return service.get_transaction_by_address(address,asset)


@jsonrpc.method("getBalance")
def get_balance(address):
    return service.get_balance(address)


@jsonrpc.method("getBlockHeight")
def get_block_height():
    return service.get_block_height()

@jsonrpc.method("transferTnc")
def faucet(addressFrom,addressTo):
    return service.faucet(addressFrom,addressTo)


@jsonrpc.method("getAllVout")
def get_vout(address,assetId):
    return service.get_all_vout(address,assetId)

@jsonrpc.method("recoverAndVerifyTx")
def recover_and_verify_tx(signedTx):
    return service.recover_and_verify_tx(signedTx)

@jsonrpc.method("verifySignature")
def verify_signature(message,signature,pubkey):
    return service.verify_signature(message,signature,pubkey)


# @jsonrpc.method("verifyTransfer")
# def verify_transfer(addressFrom,addressTo,value):
#     return service.verify_transfer(addressFrom,addressTo,value)

@jsonrpc.method("autoTransferTNC")
def transfer_tnc(addressTo,value):
    passwd=request.headers.get("Password")
    remote_ip=request.remote_addr
    print(remote_ip)
    passwd_hash=setting.PASSWD_HASH
    address_from=setting.FUNDING_ADDRESS
    privt_key=setting.PRIVTKEY
    res = verify_password(passwd, passwd_hash)
    if remote_ip==setting.REMOTE_ADDR and res:
        return service.transfer_tnc(address_from,addressTo,value,privt_key)
    return {}