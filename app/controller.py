import time

from decimal import Decimal
from flask import request
from app import jsonrpc
from app import service
from .utils import verify_password

from config import setting


@jsonrpc.method("constructTx")
def construct_tx(addressFrom,addressTo,value,assetId):
    if assetId.lower() == setting.NNC_ASSETID:
        decimals = 2
        value = int(Decimal(value) * pow(10, decimals))
    elif assetId.lower() in [setting.GAS_ASSETID,setting.NEO_ASSETID]:
        value = float(value)
    else:
        decimals = 8
        value = int(Decimal(value) * pow(10, decimals))

    return service.construct_tx(addressFrom,addressTo,value,assetId)

@jsonrpc.method("constructTx_2")
def construct_tx_2(addressFrom,addressTo,value,assetId):
    value = float(value)
    return service.construct_tx(addressFrom,addressTo,value,assetId)


@jsonrpc.method("sign")
def sign(txData,privtKey):
    return service.sign(txData,privtKey)


@jsonrpc.method("sendRawTx")
def send_raw_tx(rawTx):
    return service.send_raw_tx(rawTx)


@jsonrpc.method("signAndBroadcast")
def sign_and_broadcast(txData,privtKey):
    return service.sign_and_broadcast(txData,privtKey)

@jsonrpc.method("getApplicationLog")
def get_application_log(txid):
    return service.get_application_log(txid)

@jsonrpc.method("getTransactionHeight")
def get_transaction_height(txid):
    return service.get_transaction_height(txid)

# @jsonrpc.method("getTransactionByAddress")
# def get_transaction_by_address(address,asset,page=1):
#     return service.get_transaction_by_address(address,asset,page)


@jsonrpc.method("getTransactionByAddress")
def get_transaction_by_address(address,asset,page=1):
    return service.get_transaction_by_address(address,asset,page)


@jsonrpc.method("getClaimTx")
def get_claim_tx(address,page=1):
    return service.get_claim_tx(address,page)

@jsonrpc.method("getTokenInfo")
def get_token_info(queryWord):
    return service.get_token_info(queryWord)

@jsonrpc.method("getTokenHolding")
def get_token_holding(address):
    return service.get_token_holding(address)


@jsonrpc.method("getBalance")
def get_balance(address,assetId=None):
    return service.get_balance(address,assetId)

@jsonrpc.method("getBalance_2")
def get_balance_2(address,assetIdList):
    return service.get_balance_2(address,assetIdList)


@jsonrpc.method("getBlockHeight")
def get_block_height():
    return service.get_block_height()

@jsonrpc.method("transferTnc")
def faucet(addressFrom,addressTo):
    return service.faucet(addressFrom,addressTo)


@jsonrpc.method("getUtxo")
def get_neo_vout(address,asset_id,amount):
    return service.get_neo_vout(address,amount,asset_id)



@jsonrpc.method("recoverAndVerifyTx")
def recover_and_verify_tx(signedTx):
    return service.recover_and_verify_tx(signedTx)

@jsonrpc.method("verifySignature")
def verify_signature(message,signature,pubkey):
    return service.verify_signature(message,signature,pubkey)



@jsonrpc.method("autoTransferTNC")
def transfer_tnc(addressTo,value):
    passwd=request.headers.get("Password")
    remote_ip = request.headers.get("X-Real-IP")
    passwd_hash=setting.PASSWD_HASH
    address_from=setting.FUNDING_ADDRESS
    privt_key=setting.PRIVTKEY
    res = verify_password(passwd, passwd_hash)
    value = int(Decimal(str(value)) * pow(10, 8))

    if remote_ip==setting.REMOTE_ADDR and res:
        return service.token_swap(address_from,addressTo,value,privt_key)
    return {}



@jsonrpc.method("autoTransfer")
def auto_transfer(addressFrom,addressTo,value,assetId,privtKey):
        return service.auto_transfer(addressFrom,addressTo,value,assetId,privtKey)


@jsonrpc.method("getClaimableGas")
def get_claimable_gas(address):
        return service.get_claimable_gas(address)

@jsonrpc.method("getUnClaimedGas")
def get_unclaimable_gas(address):
        return service.get_unclaimable_gas(address)

@jsonrpc.method("extractGas")
def extract_gas(address):
        return service.extract_gas(address)

@jsonrpc.method("transferAllNeoToSelf")
def transfer_all_neo_to_self(address,balance):
        return service.transfer_all_neo_to_self(address,balance)

# about channel

@jsonrpc.method("FunderCreate")
def create_funder(pubkeySelf,pubkeyOther,deposit,assetType):
    return service.create_funder(pubkeySelf,pubkeyOther,deposit,assetType)

@jsonrpc.method("RefoundTrans")
def refunder(addressFunding,balanceSelf,balanceOther,pubkeySelf,pubkeyOther,scriptFunding,assetType):
    return service.refunder(addressFunding,balanceSelf,balanceOther,pubkeySelf,pubkeyOther,scriptFunding,assetType)


@jsonrpc.method("FunderTransaction")
def create_rsmc(pubkeySelf,pubkeyOther,addressFunding,scriptFunding,balanceSelf,balanceOther,foundingTxId,assetType):
    return service.create_rsmc(pubkeySelf,pubkeyOther,addressFunding,scriptFunding,balanceSelf,balanceOther,foundingTxId,assetType)

@jsonrpc.method("HTLCTransaction")
def create_htlc(pubkeySelf,pubkeyOther,htlcValue,balanceSelf,balanceOther,hash_R,addressFunding,scriptFunding,assetType):
    return service.create_htlc(pubkeySelf,pubkeyOther,htlcValue,balanceSelf,balanceOther,hash_R,addressFunding,scriptFunding,assetType)