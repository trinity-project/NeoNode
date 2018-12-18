import json
import random
import time
from collections import deque

import gevent
import requests

from app.TX.interface import createTx, createMultiTx, createFundingTx, createCTX, createRDTX, createBRTX, \
    createRefundTX, create_sender_HTLC_TXS, create_receiver_HTLC_TXS, createClaimTx
from app.TX.utils import pubkeyToAddress
from app.utils import ToScriptHash, int_to_hex, privtkey_sign, hex_reverse, privtKey_to_publicKey, \
    get_claimable_from_neoscan, get_unclaimed_from_neoscan, get_tokenholding_from_neoscan, handle_invoke_tx_decimal
from app.model import  InvokeTx, ContractTx, Vout, ClaimTx,Token
from decimal import Decimal

from sqlalchemy import or_

from config import setting
import binascii

from neo.IO import Helper
from neo.Core import Helper as CoreHelper
from neocore.Cryptography.Crypto import Crypto

from project_log.my_log import setup_mylogger

runserver_logger = setup_mylogger(logfile="runserver.log")

def construct_raw_tx(txData,signature,publicKey):
    rawData=txData+"01"+"41"+"40"+signature+"23"+"21"+publicKey+"ac"
    return rawData



def async_send_raw_tx(rawTx):
    try:
        verify_res = recover_and_verify_tx(rawTx).get("verify")
    except:
        verify_res = False
    if verify_res:
        import threading
        t = threading.Thread(target=send_raw_tx, args=(rawTx,))  # 创建线程
        t.setDaemon(True)  # 设置为后台线程，这里默认是False，设置为True之后则主线程不用等待子线程
        t.start()  # 开启线程
        return True
    else:
        return False


def send_raw_tx(rawTx):

    data = {
        "jsonrpc": "2.0",
        "method": "sendrawtransaction",
        "params": [rawTx],
        "id": 1
    }
    try:
        url = random.choice(setting.NEOCLIURL)
        res = requests.post(url,json=data).json()
        if res.get("result"):
            return True
        return False
    except Exception as e:
        runserver_logger.error(e)
        return False


def sign(txData,privtKey):
    signature = privtkey_sign(txData,privtKey)

    return signature


def sign_and_broadcast(txData,privtKey):
    signature = privtkey_sign(txData, privtKey)
    pubkey = privtKey_to_publicKey(privtKey)
    raw_tx = construct_raw_tx(txData,signature,pubkey)
    return send_raw_tx(raw_tx)


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


def _get_nep5_balance(address,assetId):
    data = {
        "jsonrpc": "2.0",
        "method": "invokefunction",
        "params": [
            assetId,
            "balanceOf",
            [
                {
                    "type": "Hash160",
                    "value": ToScriptHash(address).ToString()
                }
            ]
        ],
        "id": 1
    }
    try:
        res = requests.post(random.choice(setting.NEOCLIURL), json=data).json()
        value = res["result"]["stack"][0]["value"]
    except:
        value = 0

    return value


def _get_global_asset(address):
    data = {
        "jsonrpc": "2.0",
        "method": "getaccountstate",
        "params": [address],
        "id": 1
    }
    try:
        res = requests.post(random.choice(setting.NEOCLIURL), json=data).json()
        balances = res["result"]["balances"]
    except:
        balances = None

    return balances


def _get_balance(address,assetId):
    token=Token.query.filter(Token.address==assetId).first()
    if not token:
        balances = _get_global_asset(address)
        if balances:
            for balance in balances:
                if balance.get("asset") == assetId:
                    return {
                        "assetId":assetId,
                        "balance":balance.get("value")
                    }

        return {
            "assetId": assetId,
            "balance": "0"
        }
    else:
        try:
            res = _get_nep5_balance(address,assetId)
            value = int(hex_reverse(res),16) if res else 0
            return {
                "assetId": assetId,
                "balance": str(value)
            }
        except:
            return {
                "assetId": assetId,
                "balance": "0"
            }


def get_balance(address,assetId):
    neo_balance = 0
    gas_balance = 0
    balances = _get_global_asset(address)
    if balances:
        for balance in balances:
            if balance.get("asset") == setting.NEO_ASSETID:
                neo_balance = balance.get("value")
            elif balance.get("asset") == setting.GAS_ASSETID:
                gas_balance = balance.get("value")

    if not assetId:
        value = _get_nep5_balance(address,setting.CONTRACTHASH)


        response={
            "gasBalance":float(Decimal(gas_balance)),
            "neoBalance":int(neo_balance),
            "tncBalance":float(Decimal(int(hex_reverse(value), 16)) / (10**8)) if value else 0
        }

        return response

    else:
        if assetId ==setting.NEO_ASSETID:
            return neo_balance
        elif assetId == setting.GAS_ASSETID:
            return float(Decimal(gas_balance))
        else:
            try:
                res = _get_nep5_balance(address,assetId)
                value = float(Decimal(int(hex_reverse(res), 16))) if res else 0
                return value
            except:
                return 0


def get_balance_2(address,assetIdList):
    task_list = []
    for assetId in assetIdList:
        task_list.append(gevent.spawn(_get_balance, address,assetId))

    task_results = gevent.joinall(task_list)

    return [task_result.value for task_result in task_results]


def get_application_log(txid):
    data = {
        "jsonrpc": "2.0",
        "method": "getapplicationlog",
        "params": [txid],
        "id": 1
    }
    res = requests.post(random.choice(setting.NEOCLIURL), json=data).json()
    try:
        vmstate = res["result"]["executions"][0].get("vmstate")
        vmstate = True if vmstate == "HALT, BREAK" else False
        return vmstate
    except:
        return None


def get_block_height():
    data = {
        "jsonrpc": "2.0",
        "method": "getblockcount",
        "params": [],
        "id": 1
    }
    res = requests.post(random.choice(setting.NEOCLIURL), json=data).json()
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


def get_transaction_by_address(address,asset,page=1):
    if asset==setting.NEO_ASSETID or asset==setting.GAS_ASSETID:
        try:
            query_tx=ContractTx.query.filter(
                or_(ContractTx.address_from==address,ContractTx.address_to==address),
                ContractTx.asset==asset,
                ).order_by(ContractTx.block_timestamp.desc()).paginate(page=page,per_page=8).items

        except:
            query_tx = []

        decimal = 0

    else:
        try:
            query_tx = InvokeTx.query.filter(
                or_(InvokeTx.address_from == address, InvokeTx.address_to == address),
                InvokeTx.contract == asset
            ).order_by(InvokeTx.block_timestamp.desc()).paginate(page=page,per_page=8).items
        except Exception as e:
            runserver_logger.error(e)
            query_tx = []
        if query_tx:
            exist_instance = Token.query_token(address=asset)
            if exist_instance:
                decimal = int(exist_instance.decimal)

            else:
                decimal = 0
    txs = [handle_invoke_tx_decimal(item.to_json(),decimal) for item in query_tx]

    return txs


def get_claim_tx(address,page):

    query_tx = ClaimTx.query.filter(ClaimTx.address_to == address).\
        order_by(ClaimTx.block_timestamp.desc()).paginate(page=page, per_page=8).items

    return [item.to_json() for item in query_tx]


def get_token_info(queryWord):
    length_of_query_word=len(queryWord)

    if length_of_query_word==42 or length_of_query_word==40:
        queryWord=queryWord if length_of_query_word ==42 else "0x"+queryWord
        query_res = Token.query_token(address=queryWord)
    else:
        queryWord = queryWord.upper()
        query_res = Token.query_token(symbol=queryWord)

    if query_res:
        return [query_res.toJson()]
    return []

def get_token_holding(address):
    holding_list = get_tokenholding_from_neoscan(address)
    res = deque([])
    for holding in holding_list:
        query_res = Token.query_token(address="0x"+holding.get("asset_hash"))
        if query_res:
            tmp_dict = query_res.toJson()
            tmp_dict["balance"] = int(holding.get("amount")*(10** int(tmp_dict["tokenDecimal"])))
            # if tmp_dict["balance"] == 0:
            #     continue
            if tmp_dict.get("tokenIcon"):
                res.appendleft(tmp_dict)
            else:
                res.append(tmp_dict)

    balances = _get_global_asset(address)
    if balances:
        for balance in balances:
            if balance.get("asset") == setting.NEO_ASSETID:
                res.appendleft(dict(balance=balance.get("value"),tokenAddress=balance.get("asset"),
                                    tokenDecimal="0",tokenIcon=None,tokenName="NEO",
                                    tokenSynbol="NEO",tokenType="NEO"))

            if balance.get("asset") == setting.GAS_ASSETID:
                res.appendleft(dict(balance=str(Decimal(balance.get("value"))*(10**8)),tokenAddress=balance.get("asset"),
                                    tokenDecimal="8",tokenIcon=None,tokenName="GAS",
                                            tokenSynbol="GAS",tokenType="NEO"))
    else:
        res.appendleft(dict(balance="0", tokenAddress="0xc56f33fc6ecfcd0c225c4ab356fee59390af8560be0e930faebe74a6daff7c9b",
                            tokenDecimal="0", tokenIcon=None, tokenName="NEO",
                            tokenSynbol="NEO", tokenType="NEO"))
        res.appendleft(dict(balance="0", tokenAddress="0x602c79718b16e442de58778e148d0b1084e3b2dffd5de6b7b16cee7969282de7",
                            tokenDecimal="8", tokenIcon=None, tokenName="GAS",
                            tokenSynbol="GAS", tokenType="NEO"))
    return list(res)


def faucet(addressFrom,addressTo):
    tx_data=construct_tx(addressFrom=addressFrom,addressTo=addressTo,
                         value=10,assetId="0x849d095d07950b9e56d0c895ec48ec5100cfdff1")
    tx_id = tx_data["txid"]
    signature=sign(txData=tx_data["txData"],
                  privtKey="0d94b060fe4a5f382174f75f3dca384ebc59c729cef92d553084c7c660a4c08f")
    publicKey = "023886d5529481223f94d422bb6a1e05b0f831e2628c3200373a986b8208ff1c26"
    raw_data = tx_data["txData"] + "01" + "41" + "40" + signature + "23" + "21" + publicKey + "ac"
    response=send_raw_tx(raw_data)
    if response:
        return tx_id
    else:
        return None

def token_swap(addressFrom,addressTo,value,privtKey):
    tx_data=construct_tx(addressFrom=addressFrom,addressTo=addressTo,value=value,assetId=setting.CONTRACTHASH)
    tx_id = tx_data["txid"]
    signature=sign(txData=tx_data["txData"],privtKey=privtKey)
    publicKey = privtKey_to_publicKey(privtKey)
    raw_data=tx_data["txData"]+"01"+"41"+"40"+signature+"23"+"21"+publicKey+"ac"
    response=send_raw_tx(raw_data)
    if response:
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
    return result





def auto_transfer(addressFrom,addressTo,value,assetId,privtKey):
    res = createTx(addressFrom, addressTo, value, assetId)
    tx_data = res.get("txData")
    tx_id = res.get("txid")
    signature = privtkey_sign(tx_data,privtKey)
    publicKey = privtKey_to_publicKey(privtKey)
    raw_data = tx_data + "01" + "41" + "40" + signature + "23" + "21" + publicKey + "ac"
    return tx_id,send_raw_tx(raw_data)


def get_claimable_gas(address):
    res = get_claimable_from_neoscan(address)
    return res[0]


def get_unclaimed_gas(address):
    res = get_unclaimed_from_neoscan(address)
    return res


def extract_gas(address):
    res = get_claimable_from_neoscan(address)
    if res[0] ==0 and res[1] ==[]:
        raise Exception("no claimble gas")
    return createClaimTx(address=address,value=res[0],claims=res[1])


def transfer_all_neo_to_self(address,balance):
    res=createTx(address,address,balance,setting.NEO_ASSETID)
    return res



def create_funder(pubkeySelf,pubkeyOther,deposit,assetType):
    walletSelf= {
        "pubkey":pubkeySelf,
        "deposit":deposit
    }
    walletOther= {
        "pubkey":pubkeyOther,
        "deposit":deposit
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
    revocabledelivery = createRDTX(commitment.get("addressRSMC"), address_self, float(walletSelf["deposit"]),
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

    BR_tx = createBRTX(C_tx["addressRSMC"], pubkeyToAddress(pubkeyOther), balanceSelf, C_tx["scriptRSMC"], C_tx["txId"], assertId)

    return {"C_TX":C_tx,"R_TX":RD_tx,"BR_TX":BR_tx}



def create_htlc(pubkeySelf,pubkeyOther,htlcValue,balanceSelf,balanceOther,hash_R,addressFunding,scriptFunding,assetType):

    if assetType=="NEO":
        assertId=setting.NEO_ASSETID
    elif assetType=="GAS":
        assertId=setting.GAS_ASSETID
    else:
        assertId=setting.CONTRACTHASH

    sender_htlc_txs=create_sender_HTLC_TXS(pubkeySelf, pubkeyOther, htlcValue, balanceSelf,
                              balanceOther, hash_R, addressFunding,
                              scriptFunding, assertId)

    receiver_htlc_tx=create_receiver_HTLC_TXS( pubkeySelf,
                                               pubkeyOther,
                                               htlcValue,
                                               balanceSelf,
                                               balanceOther,
                                               hash_R,
                                               addressFunding,
                                               scriptFunding,
                                               assertId)

    both_side_txs={}
    both_side_txs.update(sender_htlc_txs)
    both_side_txs.update(receiver_htlc_tx)

    return both_side_txs