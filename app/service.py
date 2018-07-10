import json
import time

import requests

from app.TX.interface import createTx, createMultiTx, createFundingTx, createCTX, createRDTX, createBRTX, \
    createRefundTX, create_sender_HTLC_TXS
from app.TX.utils import pubkeyToAddress
from app.utils import  ToScriptHash, int_to_hex, privtkey_sign, hex_reverse,privtKey_to_publicKey
from app.model import Balance, InvokeTx, ContractTx, Vout
from decimal import Decimal

from sqlalchemy import or_

from config import setting
import binascii

from neo.IO import Helper
from neo.Core import Helper as CoreHelper
from neocore.Cryptography.Crypto import Crypto



def construct_raw_tx(txData,signature,publicKey):
    rawData=txData+"01"+"41"+"40"+signature+"23"+"21"+publicKey+"ac"
    return rawData



def send_raw_tx(rawTx):
    data = {
        "jsonrpc": "2.0",
        "method": "sendrawtransaction",
        "params": [rawTx],
        "id": 1
    }
    res = requests.post(setting.NEOCLIURL,json=data).json()
    if res["result"]:
        return "success"
    return "fail"

def sign(txData,privtKey):
    signature = privtkey_sign(txData,privtKey)
    print("signature:",signature)
    publicKey=privtKey_to_publicKey(privtKey)
    rawData=txData+"01"+"41"+"40"+signature+"23"+"21"+publicKey+"ac"
    return rawData

def multi_sign(txData,privtKey1,privtKey2,verificationScript):
    signature1 = privtkey_sign(txData, privtKey1)
    signature2 = privtkey_sign(txData, privtKey2)
    invoke_script = int_to_hex(len(signature1) / 2) + signature1 + int_to_hex(len(signature2) / 2) + signature2

    txData+="01"         #witness length
    txData+=int_to_hex(len(invoke_script)/2)
    txData+=invoke_script
    txData+=int_to_hex(len(verificationScript)/2)
    txData+=verificationScript
    raw_data=txData
    return raw_data

def get_balance(address):
    balance=Balance.query.filter_by(address=address).first()

    data = {
        "jsonrpc": "2.0",
        "method": "invokefunction",
        "params": [
            setting.CONTRACTHASH,
            "balanceOf",
            [
                {
                    "type":"Hash160",
                    "value":ToScriptHash(address).ToString()
                }
            ]
        ],
        "id": 1
    }
    res = requests.post(setting.NEOCLIURL, json=data).json()
    try:
        value=res["result"]["stack"][0]["value"]
    except:
        value=0
    if balance:
        response={
            "gasBalance":float(balance.gas_balance),
            "neoBalance":float(balance.neo_balance),
            "tncBalance":int(hex_reverse(value),16)/100000000 if value else 0
        }
    else:
        response={
            "tncBalance":int(hex_reverse(value),16)/100000000 if value else 0,
            "gasBalance":0,
            "neoBalance":0
        }

    return response

def get_block_height():
    data = {
        "jsonrpc": "2.0",
        "method": "getblockcount",
        "params": [],
        "id": 1
    }
    res = requests.post(setting.NEOCLIURL, json=data).json()
    try:
        return res["result"]-1
    except:
        return None

def get_transaction(txid):
    contract_tx=ContractTx.query.filter_by(tx_id=txid).first()
    if contract_tx:
        return contract_tx.to_json()

    invoke_tx=InvokeTx.query.filter_by(tx_id=txid).first()
    if invoke_tx:
        return invoke_tx.to_json()
    return None


def get_transaction_by_address(address,asset,timestamp=None,page=1):
    if asset==setting.NEO_ASSETID or asset==setting.GAS_ASSETID:
        timestamp_filter=ContractTx.block_timestamp >=timestamp if timestamp else ""

        query_tx=ContractTx.query.filter(
            or_(ContractTx.address_from==address,ContractTx.address_to==address),
            ContractTx.asset==asset,
            timestamp_filter
            ).order_by(ContractTx.block_timestamp.desc()).paginate(page=page,per_page=8).items
    elif asset==setting.CONTRACTHASH:
        timestamp_filter=InvokeTx.block_timestamp >=timestamp if timestamp else ""

        query_tx = InvokeTx.query.filter(
            or_(InvokeTx.address_from == address, InvokeTx.address_to == address),
            timestamp_filter
        ).order_by(InvokeTx.block_timestamp.desc()).paginate(page=page,per_page=8).items


    else:
        query_tx=[]


    return [item.to_json() for item in query_tx]


def faucet(addressFrom,addressTo):
    tx_data=construct_tx(addressFrom=addressFrom,addressTo=addressTo,
                         value=10,assetId="0x849d095d07950b9e56d0c895ec48ec5100cfdff1")
    tx_id = tx_data["txid"]
    print(tx_data['txData'])
    raw_data=sign(txData=tx_data["txData"],
                  privtKey="0d94b060fe4a5f382174f75f3dca384ebc59c729cef92d553084c7c660a4c08f")
    response=send_raw_tx(raw_data)
    if response=="success":
        return tx_id
    else:
        return None

def transfer_tnc(addressFrom,addressTo,value,privtKey):
    tx_data=construct_tx(addressFrom=addressFrom,addressTo=addressTo,value=value,assetId=setting.CONTRACTHASH)
    tx_id = tx_data["txid"]
    raw_data=sign(txData=tx_data["txData"],privtKey=privtKey)
    response=send_raw_tx(raw_data)
    if response=="success":
        return {
            "txId":tx_id
        }
    else:
        return None




def construct_tx(addressFrom,addressTo,value,assetId):
    res=createTx(addressFrom,addressTo,value,assetId)
    return res





def construct_multi_tx(addressFrom,addressTo,value,assetId):
    res=createMultiTx(addressFrom,addressTo,value,assetId)
    return res



def get_vout(address,amount):
    items=Vout.query.filter_by(address=address).order_by(Vout.value.desc()).all()
    if items:
        tmplist=[]
        totalvalue=0
        for item in items:
            if item.value>=amount:
                return [(item.tx_id,float(item.value),item.vout_number)]
            tmplist.append((item.tx_id,float(item.value),item.vout_number))
            totalvalue+=item.value
            if totalvalue>=amount:
                return tmplist

    return []


def get_all_vout(address,assetid):
    items=Vout.query.filter_by(address=address,asset_id=assetid).order_by(Vout.value.desc()).all()
    if items:
        return [(item.tx_id,float(item.value),item.vout_number) for item in items]

    return []


def recover_and_verify_tx(signedTx):

    data_bytes = binascii.unhexlify(signedTx.encode())

    tx_object = Helper.Helper.DeserializeTX(data_bytes)
    tx_json = tx_object.ToJson()
    res = CoreHelper.Helper.VerifyScripts(tx_object)

    for item in tx_json.get("vout"):
        if isinstance(item["address"],bytes):
            item["address"]=item["address"].decode()
    return {
        "verify":res,
        "recover_json":tx_json
    }


def verify_signature(message,signature,pubkey):
    signature=binascii.unhexlify(signature.encode())
    pubkey=binascii.unhexlify(pubkey.encode())
    result = Crypto.VerifySignature(message, signature, pubkey)
    return {
        "result":result
    }


def create_funder(pubkeySelf,pubkeyOther,depoist,assetType):
    walletSelf= {
        "pubkey":pubkeySelf,
        "deposit":depoist
    }
    walletOther= {
        "pubkey":pubkeyOther,
        "deposit":depoist
    }

    if assetType=="NEO":
        assertId=setting.NEO_ASSETID
    elif assetType=="GAS":
        assertId=setting.GAS_ASSETID
    else:
        assertId=setting.CONTRACTHASH


    founder=createFundingTx(walletSelf,walletOther,assertId)
    commitment = createCTX(founder.get("addressFunding"), float(walletSelf["deposit"]), float(walletOther["deposit"]),walletSelf["pubkey"],
                           walletOther["pubkey"], founder.get("scriptFunding"), assertId, founder.get('txId'))
    address_self = pubkeyToAddress(walletSelf["pubkey"])
    revocabledelivery = createRDTX(commitment.get("addressRSMC"), address_self, float(walletSelf[depoist]),
                                   commitment.get("txId"),
                                   commitment.get("scriptRSMC"), assertId)
    return {"Founder": founder, "C_TX": commitment, "R_TX": revocabledelivery}


def refunder(addressFunding,balanceSelf,balanceOther,pubkeySelf,pubkeyOther,scriptFunding,assetType):

    if assetType=="NEO":
        assertId=setting.NEO_ASSETID
    elif assetType=="GAS":
        assertId=setting.GAS_ASSETID
    else:
        assertId=setting.CONTRACTHASH
    refund_tx = createRefundTX(addressFunding,balanceSelf,balanceOther,pubkeySelf,pubkeyOther,scriptFunding,assertId)

    return {
        "Settlement":refund_tx
    }




def create_rsmc(pubkeySelf, pubkeyOther, addressFunding, scriptFunding, balanceSelf,balanceOther, foundingTxId, assetType):

    if assetType=="NEO":
        assertId=setting.NEO_ASSETID
    elif assetType=="GAS":
        assertId=setting.GAS_ASSETID
    else:
        assertId=setting.CONTRACTHASH

    C_tx = createCTX(addressFunding=addressFunding, balanceSelf=balanceSelf,
                          balanceOther=balanceOther, pubkeySelf=pubkeySelf,
                          pubkeyOther=pubkeyOther, fundingScript=scriptFunding, asset_id=assertId,fundingTxId=foundingTxId)

    RD_tx = createRDTX(addressRSMC=C_tx["addressRSMC"], addressSelf=pubkeyToAddress(pubkeySelf),
                            balanceSelf=balanceSelf, CTxId=C_tx["txId"],
                            RSMCScript=C_tx["scriptRSMC"], asset_id=assertId)

    return {"C_TX":C_tx,"R_TX":RD_tx}



def create_htlc(pubkeySelf,pubkeyOther,htlcValue,balanceSelf,balanceOther,hash_R,addressFunding,scriptFunding,assetType):

    if assetType=="NEO":
        assertId=setting.NEO_ASSETID
    elif assetType=="GAS":
        assertId=setting.GAS_ASSETID
    else:
        assertId=setting.CONTRACTHASH

    return create_sender_HTLC_TXS(pubkeySelf, pubkeyOther, htlcValue, balanceSelf,
                              balanceOther, hash_R, addressFunding,
                              scriptFunding, assertId)


