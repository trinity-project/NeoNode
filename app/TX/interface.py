import binascii
import time

import requests
from decimal import Decimal
from neocore.Fixed8 import Fixed8
from neocore.UInt256 import UInt256

from app.TX.MyTransaction import InvocationTransaction, ContractTransaction, TransactionInput, TransactionOutput
from app.TX.TransactionAttribute import TransactionAttribute, TransactionAttributeUsage
from app.model import Balance, Vout
from app.utils import ToScriptHash
from config import setting
from app.TX.utils import hex_reverse, ToAddresstHash, createTxid, createMultiSigContract, create_opdata, \
    createRSMCContract, str_reverse


#RSMC
def createFundingTx(walletSelf,walletOther): #qian ming shi A de qian min zai hou
    '''

    :param walletSelf: dict {
            "pubkey":"",
            "address":"",
            "deposit":0
    }
    :param walletOhter: dict {
            "pubkey":"",
            "address":"",
            "deposit":0
    :return:
    '''

    multi_contract = createMultiSigContract([walletSelf["pubkey"],walletOther["pubkey"]])
    contractAddress = multi_contract["address"]
    time_stamp = TransactionAttribute(usage=TransactionAttributeUsage.Remark,
                                      data=bytearray.fromhex(hex(int(time.time()))[2:]))
    address_hash_self = TransactionAttribute(usage=TransactionAttributeUsage.Script,
                                         data=ToAddresstHash(walletSelf["address"]).Data)
    address_hash_other = TransactionAttribute(usage=TransactionAttributeUsage.Script,
                                         data=ToAddresstHash(walletOther["address"]).Data)
    txAttributes = [address_hash_self, address_hash_other, time_stamp]

    op_dataSelf = create_opdata(address_from=walletSelf["address"], address_to=contractAddress, value=walletSelf["deposit"],
                             contract_hash=setting.CONTRACTHASH)
    op_dataOther = create_opdata(address_from=walletOther["address"], address_to=contractAddress, value=walletOther["deposit"],
                             contract_hash=setting.CONTRACTHASH)

    tx = InvocationTransaction()
    tx.Version = 1
    tx.Attributes = txAttributes
    tx.Script = binascii.unhexlify(op_dataSelf + op_dataOther)

    return {
        "txData":tx.get_tx_data(),
        "addressFunding":contractAddress,
        "script":multi_contract["script"],
        "txId": createTxid(tx.get_tx_data())
    }


def createCTX(addressFunding,addressSelf,balanceSelf,addressOther,balanceOther,pubkeySelf,pubkeyOther):
    RSMCContract=createRSMCContract(hashSelf=ToAddresstHash(addressSelf).ToString2(),pubkeySelf=pubkeySelf,
                       hashOther=ToAddresstHash(addressOther).ToString2(),pubkeyOther=pubkeyOther,magicTimestamp=time.time())
    time_stamp = TransactionAttribute(usage=TransactionAttributeUsage.Remark,
                                      data=bytearray.fromhex(hex(int(time.time()))[2:]))
    address_hash_funding = TransactionAttribute(usage=TransactionAttributeUsage.Script,
                                         data=ToAddresstHash(addressFunding).Data)
    txAttributes = [address_hash_funding, time_stamp]

    op_data_to_RSMC = create_opdata(address_from=addressFunding, address_to=RSMCContract["address"], value=balanceSelf,contract_hash=TNC)
    op_data_to_other = create_opdata(address_from=addressFunding, address_to=addressOther, value=balanceOther,contract_hash=TNC)

    tx = InvocationTransaction()
    tx.Version = 1
    tx.Attributes = txAttributes
    tx.Script = binascii.unhexlify(op_data_to_RSMC+op_data_to_other)

    return {
        "txData":tx.get_tx_data(),
        "addressRSMC":RSMCContract["address"],
        "script":RSMCContract["script"],
        "txid":createTxid(tx.get_tx_data())
    }

def createRDTX(addressRSMC,addressSelf,balanceSelf,CTxId):

    time_stamp = TransactionAttribute(usage=TransactionAttributeUsage.Remark,
                                      data=bytearray.fromhex(hex(int(time.time()))[2:]))
    address_hash_RSMC = TransactionAttribute(usage=TransactionAttributeUsage.Script,
                                         data=ToAddresstHash(addressRSMC).Data)
    pre_txid = TransactionAttribute(usage=TransactionAttributeUsage.Remark1, data=bytearray.fromhex(
        hex_reverse(CTxId)))

    outputTo= TransactionAttribute(usage=TransactionAttributeUsage.Remark2, data=ToAddresstHash(addressSelf).Data)

    txAttributes = [address_hash_RSMC, time_stamp,pre_txid,outputTo]

    op_data_to_self = create_opdata(address_from=addressRSMC, address_to=addressSelf, value=balanceSelf,contract_hash=TNC)


    tx = InvocationTransaction()
    tx.Version = 1
    tx.Attributes = txAttributes
    tx.Script = binascii.unhexlify(op_data_to_self)

    return tx.get_tx_data()


def createBRTX(addressRSMC,addressOther,balanceSelf):

    time_stamp = TransactionAttribute(usage=TransactionAttributeUsage.Remark,
                                      data=bytearray.fromhex(hex(int(time.time()))[2:]))
    address_hash_RSMC = TransactionAttribute(usage=TransactionAttributeUsage.Script,
                                         data=ToAddresstHash(addressRSMC).Data)
    outputTo = TransactionAttribute(usage=TransactionAttributeUsage.Remark1, data=ToAddresstHash(addressOther).Data)
    txAttributes = [address_hash_RSMC, time_stamp,outputTo]

    op_data_to_other = create_opdata(address_from=addressRSMC, address_to=addressOther, value=balanceSelf,contract_hash=TNC)


    tx = InvocationTransaction()
    tx.Version = 1
    tx.Attributes = txAttributes
    tx.Script = binascii.unhexlify(op_data_to_other)

    return tx.get_tx_data()

#COMMON
def createTx(addressFrom,addressTo,value,assetId):
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
        tx.Script = binascii.unhexlify(op_data)

        return {
            "txData": tx.get_tx_data(),
            "txid": createTxid(tx.get_tx_data()),
            "witness":"014140{signature}2321{pubkey}ac"
        }

    elif assetId == setting.NEO_ASSETID or assetId == setting.GAS_ASSETID:
        if not _check_balance(address=addressFrom,assetId=assetId,value=value):
            return {}



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
            "txId": createTxid(tx.get_tx_data()),
            "witness": "014140{signature}2321{pubkey}ac"
        }

    else:

        return {}


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
        return {"message":"asset not exist"}


def _check_balance(address,assetId,value):
    balance = Balance.query.filter_by(address=address).first()
    if balance:
        if assetId == setting.GAS_ASSETID or assetId == setting.NEO_ASSETID:
            gas=balance.gas_balance
            if gas < Decimal(str(value)):
                return False
            return True


        elif assetId == setting.NEO_ASSETID:
            neo=balance.neo_balance
            if neo < Decimal(str(value)):
                return False
            return True
        elif assetId == setting.CONTRACTHASH:
            tnc=_get_tnc_balance(address)
            if tnc < value:
                return False
            return True
    return False

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
    res = requests.post(setting.NEOCLIURL, json=data).json()
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
                input =_createInput(preHash=item.tx_id,preIndex=item.vout_number)
                inputs.append(input)
                inputs_total+=float(item.value)
                return inputs,inputs_total
            else:
                input =_createInput(preHash=item.tx_id,preIndex=item.vout_number)
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

