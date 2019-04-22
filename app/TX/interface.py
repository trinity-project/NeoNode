import binascii
import random
import time

import requests
from decimal import Decimal
from neocore.Fixed8 import Fixed8
from neocore.UInt256 import UInt256

from app.TX.MyTransaction import InvocationTransaction, ContractTransaction, TransactionInput, TransactionOutput,ClaimTransaction
from app.TX.TransactionAttribute import TransactionAttribute, TransactionAttributeUsage
from app.utils import ToScriptHash
from config import setting
from app.TX.utils import hex_reverse, ToAddresstHash, createTxid, createMultiSigContract, create_opdata, \
    createRSMCContract, str_reverse
from app.TX.adapter import neo_factory,gas_factory,tnc_factory

#RSMC


def createFundingTx(walletSelf, walletOther, asset_id):

    '''

    :param walletSelf: dict {
            "pubkey":"",
            "deposit":0
    }
    :param walletOhter: dict {
            "pubkey":"",
            "deposit":0
    :return:
    '''

    if asset_id == setting.NEO_ASSETID:
        return neo_factory.createFundingTx(walletSelf, walletOther, asset_id)

    elif asset_id == setting.GAS_ASSETID:
        return gas_factory.createFundingTx(walletSelf, walletOther, asset_id)

    else:
        return tnc_factory.createFundingTx(walletSelf, walletOther, asset_id)

def createCTX(
        addressFunding,
        balanceSelf,
        balanceOther,
        pubkeySelf,
        pubkeyOther,
        fundingScript,
        asset_id,
        fundingTxId):
    if asset_id == setting.NEO_ASSETID:
        return neo_factory.createCTX(
            balanceSelf,
            balanceOther,
            pubkeySelf,
            pubkeyOther,
            fundingScript,
            asset_id,
            fundingTxId)

    elif asset_id == setting.GAS_ASSETID:
        return gas_factory.createCTX(
            balanceSelf,
            balanceOther,
            pubkeySelf,
            pubkeyOther,
            fundingScript,
            asset_id,
            fundingTxId)
    else:
        # default operations tokens like TNC
        return tnc_factory.createCTX(
            addressFunding,
            balanceSelf,
            balanceOther,
            pubkeySelf,
            pubkeyOther,
            fundingScript,
            asset_id)


def createRDTX(
        addressRSMC,
        addressSelf,
        balanceSelf,
        CTxId,
        RSMCScript,
        asset_id):

    if asset_id == setting.NEO_ASSETID:
        return neo_factory.createRDTX(
            addressSelf, balanceSelf, CTxId, RSMCScript, asset_id)

    elif asset_id == setting.GAS_ASSETID:
        return gas_factory.createRDTX(
            addressSelf, balanceSelf, CTxId, RSMCScript, asset_id)
    else:
        return tnc_factory.createRDTX(
            addressRSMC,
            addressSelf,
            balanceSelf,
            CTxId,
            RSMCScript,
            asset_id)


def createBRTX(addressRSMC, addressOther, balanceSelf, RSMCScript, CTxId, asset_id):

    if asset_id == setting.NEO_ASSETID:
        return neo_factory.createBRTX(
            addressOther, balanceSelf, RSMCScript, CTxId, asset_id)

    elif asset_id == setting.GAS_ASSETID:
        return gas_factory.createBRTX(
            addressOther, balanceSelf, RSMCScript, CTxId, asset_id)
    else:
        return tnc_factory.createBRTX(
            addressRSMC,
            addressOther,
            balanceSelf,
            RSMCScript,
            asset_id)


def createRefundTX(
        addressFunding,
        balanceSelf,
        balanceOther,
        pubkeySelf,
        pubkeyOther,
        fundingScript,
        asset_id):

    if asset_id == setting.NEO_ASSETID:
        return neo_factory.createRefundTX(
            addressFunding,
            balanceSelf,
            balanceOther,
            pubkeySelf,
            pubkeyOther,
            fundingScript,
            asset_id)

    elif asset_id == setting.GAS_ASSETID:
        return gas_factory.createRefundTX(
            addressFunding,
            balanceSelf,
            balanceOther,
            pubkeySelf,
            pubkeyOther,
            fundingScript,
            asset_id)
    else:
        return tnc_factory.createRefundTX(
            addressFunding,
            balanceSelf,
            balanceOther,
            pubkeySelf,
            pubkeyOther,
            fundingScript,
            asset_id)

#==============================================================
# sender HTLC


def create_sender_HCTX(
        pubkeySender,
        pubkeyReceiver,
        HTLCValue,
        balanceSender,
        balanceReceiver,
        hashR,
        addressFunding,
        fundingScript,
        asset_id):
    if asset_id == setting.NEO_ASSETID:
        return neo_factory.create_sender_HCTX(
            pubkeySender,
            pubkeyReceiver,
            HTLCValue,
            balanceSender,
            balanceReceiver,
            hashR,
            addressFunding,
            fundingScript,
            asset_id)

    elif asset_id == setting.NEO_ASSETID:
        return gas_factory.create_sender_HCTX(
            pubkeySender,
            pubkeyReceiver,
            HTLCValue,
            balanceSender,
            balanceReceiver,
            hashR,
            addressFunding,
            fundingScript,
            asset_id)
    else:
        return tnc_factory.create_sender_HCTX(
            pubkeySender,
            pubkeyReceiver,
            HTLCValue,
            balanceSender,
            balanceReceiver,
            hashR,
            addressFunding,
            fundingScript,
            asset_id)


def create_sender_RDTX(
        addressRSMC,
        addressSender,
        balanceSender,
        senderHCTxId,
        RSMCScript,
        asset_id):
    if asset_id == setting.NEO_ASSETID:
        return neo_factory.create_sender_RDTX(
            addressSender, balanceSender, senderHCTxId, RSMCScript, asset_id)

    elif asset_id == setting.NEO_ASSETID:
        return gas_factory.create_sender_RDTX(
            addressSender, balanceSender, senderHCTxId, RSMCScript, asset_id)

    else:
        return tnc_factory.create_sender_RDTX(
            addressRSMC,
            addressSender,
            balanceSender,
            senderHCTxId,
            RSMCScript,
            asset_id)


def createHEDTX(
        addressHTLC,
        addressReceiver,
        HTLCValue,
        HTLCScript,
        senderHCTxId,
        asset_id):
    if asset_id == setting.NEO_ASSETID:
        return neo_factory.createHEDTX(
            addressReceiver,
            HTLCValue,
            HTLCScript,
            senderHCTxId,
            asset_id)

    elif asset_id == setting.NEO_ASSETID:
        return gas_factory.createHEDTX(
            addressReceiver,
            HTLCValue,
            HTLCScript,
            senderHCTxId,
            asset_id)
    else:
        return tnc_factory.createHEDTX(
            addressHTLC,
            addressReceiver,
            HTLCValue,
            HTLCScript,
            asset_id)


def createHTTX(
        addressHTLC,
        pubkeySender,
        pubkeyReceiver,
        HTLCValue,
        HTLCScript,
        senderHCTxId,
        asset_id):
    if asset_id == setting.NEO_ASSETID:
        return neo_factory.createHTTX(
            pubkeySender,
            pubkeyReceiver,
            HTLCValue,
            HTLCScript,
            senderHCTxId,
            asset_id)

    elif asset_id == setting.NEO_ASSETID:
        return gas_factory.createHTTX(
            pubkeySender,
            pubkeyReceiver,
            HTLCValue,
            HTLCScript,
            senderHCTxId,
            asset_id)
    else:
        return tnc_factory.createHTTX(
            addressHTLC,
            pubkeySender,
            pubkeyReceiver,
            HTLCValue,
            HTLCScript,
            asset_id)


def createHTRDTX(
        addressRSMC,
        addressSender,
        HTLCValue,
        HTTxId,
        RSMCScript,
        asset_id):
    if asset_id == setting.NEO_ASSETID:
        return neo_factory.createHTRDTX(
            addressSender, HTLCValue, HTTxId, RSMCScript, asset_id)

    elif asset_id == setting.NEO_ASSETID:
        return gas_factory.createHTRDTX(
            addressSender, HTLCValue, HTTxId, RSMCScript, asset_id)
    else:
        return tnc_factory.createHTRDTX(
            addressRSMC,
            addressSender,
            HTLCValue,
            HTTxId,
            RSMCScript,
            asset_id)

#==============================================================
# receiver HTLC
def create_receiver_HCTX(
        pubkeySender,
        pubkeyReceiver,
        HTLCValue,
        balanceSender,
        balanceReceiver,
        hashR,
        addressFunding,
        fundingScript,
        asset_id):
    if asset_id == setting.NEO_ASSETID:
        return neo_factory.create_receiver_HCTX(
            pubkeySender,
            pubkeyReceiver,
            HTLCValue,
            balanceSender,
            balanceReceiver,
            hashR,
            addressFunding,
            fundingScript,
            asset_id)

    elif asset_id == setting.NEO_ASSETID:
        return gas_factory.create_receiver_HCTX(
            pubkeySender,
            pubkeyReceiver,
            HTLCValue,
            balanceSender,
            balanceReceiver,
            hashR,
            addressFunding,
            fundingScript,
            asset_id)
    else:
        return tnc_factory.create_receiver_HCTX(
            pubkeySender,
            pubkeyReceiver,
            HTLCValue,
            balanceSender,
            balanceReceiver,
            hashR,
            addressFunding,
            fundingScript,
            asset_id)


def create_receiver_RDTX(
        addressRSMC,
        addressReceiver,
        balanceReceiver,
        receiver_HCTxId,
        RSMCScript,
        asset_id):
    if asset_id == setting.NEO_ASSETID:
        return neo_factory.create_receiver_RDTX(
            addressReceiver,
            balanceReceiver,
            receiver_HCTxId,
            RSMCScript,
            asset_id)

    elif asset_id == setting.NEO_ASSETID:
        return gas_factory.create_receiver_RDTX(
            addressReceiver,
            balanceReceiver,
            receiver_HCTxId,
            RSMCScript,
            asset_id)
    else:
        return tnc_factory.create_receiver_RDTX(
            addressRSMC,
            addressReceiver,
            balanceReceiver,
            receiver_HCTxId,
            RSMCScript,
            asset_id)


def createHTDTX(
        addressHTLC,
        pubkeySender,
        HTLCValue,
        HTLCScript,
        receiver_HCTxId,
        asset_id):

    if asset_id == setting.NEO_ASSETID:
        return neo_factory.createHTDTX(
            pubkeySender,
            HTLCValue,
            HTLCScript,
            receiver_HCTxId,
            asset_id)

    elif asset_id == setting.NEO_ASSETID:
        return gas_factory.createHTDTX(
            pubkeySender,
            HTLCValue,
            HTLCScript,
            receiver_HCTxId,
            asset_id)
    else:
        return tnc_factory.createHTDTX(
            addressHTLC,
            pubkeySender,
            HTLCValue,
            HTLCScript,
            asset_id)


def createHETX(
        addressHTLC,
        pubkeySender,
        pubkeyReceiver,
        HTLCValue,
        HTLCScript,
        receiver_HCTxId,
        asset_id):
    if asset_id == setting.NEO_ASSETID:
        return neo_factory.createHETX(
            pubkeySender,
            pubkeyReceiver,
            HTLCValue,
            HTLCScript,
            receiver_HCTxId,
            asset_id)

    elif asset_id == setting.NEO_ASSETID:
        return gas_factory.createHETX(
            pubkeySender,
            pubkeyReceiver,
            HTLCValue,
            HTLCScript,
            receiver_HCTxId,
            asset_id)
    else:
        return tnc_factory.createHETX(
            addressHTLC,
            pubkeySender,
            pubkeyReceiver,
            HTLCValue,
            HTLCScript,
            asset_id)


def createHERDTX(
        addressRSMC,
        addressReceiver,
        HTLCValue,
        HETxId,
        RSMCScript,
        asset_id):
    if asset_id == setting.NEO_ASSETID:
        return neo_factory.createHERDTX(
            addressReceiver, HTLCValue, HETxId, RSMCScript, asset_id)

    elif asset_id == setting.NEO_ASSETID:
        return gas_factory.createHERDTX(
            addressReceiver, HTLCValue, HETxId, RSMCScript, asset_id)

    else:
        return tnc_factory.createHERDTX(
            addressRSMC,
            addressReceiver,
            HTLCValue,
            HETxId,
            RSMCScript,
            asset_id)


def create_sender_HTLC_TXS(
        pubkeySender,
        pubkeyReceiver,
        HTLCValue,
        balanceSender,
        balanceReceiver,
        hashR,
        addressFunding,
        fundingScript,
        asset_id):
    if asset_id == setting.NEO_ASSETID:
        return neo_factory.create_sender_HTLC_TXS(
            pubkeySender,
            pubkeyReceiver,
            HTLCValue,
            balanceSender,
            balanceReceiver,
            hashR,
            addressFunding,
            fundingScript,
            asset_id)

    elif asset_id == setting.NEO_ASSETID:
        return gas_factory.create_sender_HTLC_TXS(
            pubkeySender,
            pubkeyReceiver,
            HTLCValue,
            balanceSender,
            balanceReceiver,
            hashR,
            addressFunding,
            fundingScript,
            asset_id)
    else:
        return tnc_factory.create_sender_HTLC_TXS(
            pubkeySender,
            pubkeyReceiver,
            HTLCValue,
            balanceSender,
            balanceReceiver,
            hashR,
            addressFunding,
            fundingScript,
            asset_id)


def create_receiver_HTLC_TXS(
        pubkeySender,
        pubkeyReceiver,
        HTLCValue,
        balanceSender,
        balanceReceiver,
        hashR,
        addressFunding,
        fundingScript,
        asset_id):
    if asset_id == setting.NEO_ASSETID:
        return neo_factory.create_receiver_HTLC_TXS(
            pubkeySender,
            pubkeyReceiver,
            HTLCValue,
            balanceSender,
            balanceReceiver,
            hashR,
            addressFunding,
            fundingScript,
            asset_id)

    elif asset_id == setting.NEO_ASSETID:
        return gas_factory.create_receiver_HTLC_TXS(
            pubkeySender,
            pubkeyReceiver,
            HTLCValue,
            balanceSender,
            balanceReceiver,
            hashR,
            addressFunding,
            fundingScript,
            asset_id)
    else:
        return tnc_factory.create_receiver_HTLC_TXS(
            pubkeySender,
            pubkeyReceiver,
            HTLCValue,
            balanceSender,
            balanceReceiver,
            hashR,
            addressFunding,
            fundingScript,
            asset_id)

#==============================================================
#common tx


def createTx(addressFrom,addressTo,value,assetId):


    if assetId == setting.NEO_ASSETID or assetId == setting.GAS_ASSETID:
        # if not _check_balance(address=addressFrom,assetId=assetId,value=value):
        #     raise Exception("no enough balance")
        time_stamp = TransactionAttribute(usage=TransactionAttributeUsage.Remark,
                                          data=bytearray.fromhex(hex(int(time.time()))[2:]))
        address_hash = TransactionAttribute(usage=TransactionAttributeUsage.Script,
                                             data=ToAddresstHash(addressFrom).Data)
        txAttributes = [address_hash,time_stamp]

        inputs,inputs_total=_get_inputs(address=addressFrom,assetId=assetId,value=value)

        outputs = _get_outputs(addressFrom=addressFrom,addressTo=addressTo,value=value,
                               assetId=assetId,inputs_total=inputs_total)

        tx = ContractTransaction()
        tx.inputs = inputs
        tx.outputs = outputs
        tx.Attributes = txAttributes

        return {
            "txData":tx.get_tx_data(),
            "txid": createTxid(tx.get_tx_data()),
            "witness": "014140{signature}2321{pubkey}ac"
        }

    else :

        if len(assetId) != 42:
            return {}

        time_stamp = TransactionAttribute(usage=TransactionAttributeUsage.Remark,
                                          data=bytearray.fromhex(hex(int(time.time()))[2:]))
        address_hash = TransactionAttribute(usage=TransactionAttributeUsage.Script,
                                             data=ToAddresstHash(addressFrom).Data)

        txAttributes = [address_hash,time_stamp]

        op_data = create_opdata(address_from=addressFrom, address_to=addressTo, value=value,
                                 contract_hash=assetId)
        tx = InvocationTransaction()
        tx.Version = 1
        tx.Attributes = txAttributes
        tx.Script = binascii.unhexlify(op_data)

        return {
            "txData": tx.get_tx_data(),
            "txid": createTxid(tx.get_tx_data()),
            "witness":"014140{signature}2321{pubkey}ac"
        }


def createClaimTx(address,value,claims):
    time_stamp = TransactionAttribute(usage=TransactionAttributeUsage.Remark,
                                      data=bytearray.fromhex(hex(int(time.time()))[2:]))

    txAttributes = [time_stamp]

    claims  =[_createInput(preHash=item.get("txid"),preIndex=item.get("n")) for item in claims]
    output = _createOutput(assetId=setting.GAS_ASSETID,amount=value,address=address)

    tx = ClaimTransaction()
    tx.Claims = claims
    tx.outputs = [output]
    tx.Attributes = txAttributes

    return {
        "txData": tx.get_tx_data(),
        "txid": createTxid(tx.get_tx_data()),
        "witness": "014140{signature}2321{pubkey}ac",
        "amount":str(value)
    }

def createMultiTx(addressFrom,addressTo,value,assetId):
    if assetId == setting.CONTRACTHASH:

        time_stamp = TransactionAttribute(usage=TransactionAttributeUsage.Remark,
                                          data=bytearray.fromhex(hex(int(time.time()))[2:]))
        address_hash = TransactionAttribute(usage=TransactionAttributeUsage.Script,
                                             data=ToAddresstHash(addressFrom).Data)

        txAttributes = [address_hash,time_stamp]

        op_data = create_opdata(address_from=addressFrom, address_to=addressTo, value=value,
                                 contract_hash=assetId)
        tx = InvocationTransaction()
        tx.Version = 1
        tx.Attributes = txAttributes

        tx.Script = binascii.unhexlify(op_data*3)

        return {
            "txData": tx.get_tx_data(),
            "txId": createTxid(tx.get_tx_data())
        }

    else:
        return None


def _check_balance(address,assetId,value):
    balances = _get_global_asset(address)
    balance = 0
    if balances:
        for b in balances:
            if b.get("asset") == assetId:
                balance = float(b.get("value"))
    if balance < float(value):
        return False
    return True
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


def _get_tnc_balance(address):
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
    res = requests.post(random.choice(setting.NEOCLIURL), json=data).json()
    try:
        value=res["result"]["stack"][0]["value"]
    except:
        value=0
    if value:
        value=int(str_reverse(value),16)/100000000
    else:value=0
    return value



def _get_inputs(address,assetId,value):
    inputs_total=0
    inputs=[]
    if assetId == setting.GAS_ASSETID or assetId == setting.NEO_ASSETID:
        vouts = Vout.query.filter_by(address=address,asset_id=assetId).order_by(Vout.value.desc()).all()

        for item in vouts:
            if float(item.value) >= value:
                input =_createInput(preHash=item.tx_id,preIndex=int(item.vout_number))
                inputs.append(input)
                inputs_total+=float(item.value)
                return inputs,inputs_total
            else:
                input =_createInput(preHash=item.tx_id,preIndex=int(item.vout_number))
                inputs.append(input)
                inputs_total+=float(item.value)
                if inputs_total>=value:
                    return inputs,inputs_total

    return inputs,inputs_total

def _get_outputs(addressFrom,addressTo,inputs_total,value,assetId):
    outputs=[]
    if inputs_total == value:
        output=_createOutput(assetId=assetId,amount=value,address=addressTo)
        outputs.append(output)
        return outputs
    output0 = _createOutput(assetId=assetId, amount=value, address=addressTo)
    output1 = _createOutput(assetId=assetId, amount=inputs_total-value, address=addressFrom)
    outputs.append(output0)
    outputs.append(output1)
    return outputs

def _createInput(preHash,preIndex):
    pre_hash = UInt256(data=binascii.unhexlify(hex_reverse(preHash)))
    return TransactionInput(prevHash=pre_hash, prevIndex=preIndex)

def _createOutput(assetId,amount,address):
    assetId = UInt256(data=binascii.unhexlify(hex_reverse(assetId)))
    f8amount = Fixed8.TryParse(amount, require_positive=True)
    address_hash=ToAddresstHash(address)
    return TransactionOutput(AssetId=assetId, Value=f8amount, script_hash=address_hash)

