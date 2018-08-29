import json
import random
import time
import binascii
import requests
from decimal import Decimal
from neocore.Cryptography.Crypto import Crypto
from neocore.UInt160 import UInt160

from config import setting
from data_model.account_info_model import Tx, LocalBlockCout, Vout, Balance, BlockHeight, InvokeTx, ContractTx,logger
# from plugin.redis_client import redis_client


def hex_reverse(input):
    tmp_list = []
    for i in range(0, len(input), 2):
        tmp_list.append(input[i:i + 2])
    hex_str = "".join(list(reversed(tmp_list)))
    return hex_str

def hex2address(input):
    try:
        output = Crypto.ToAddress(UInt160(data=binascii.unhexlify(bytearray(input.encode("utf8")))))
    except Exception as e:
        logger.exception(e)
        output=None


    return output

def hex2interger(input):
    tmp_list = []
    for i in range(0, len(input), 2):
        tmp_list.append(input[i:i + 2])
    hex_str = "".join(list(reversed(tmp_list)))
    output = int(hex_str, 16) / 100000000

    return output

def get_application_log(txid):

    data = {
          "jsonrpc": "2.0",
          "method": "getapplicationlog",
          "params": [txid],
          "id": 1
}

    while True:
        try:
            res = requests.post(random.choice(setting.NEO_RPC_APPLICATION_LOG),json=data).json()
            if res.get("result"):
                return res.get("result")
            else:
                logger.error("txid:{} get application log is null".format(txid))
                return None
        except Exception as e:
            logger.error(e)
            time.sleep(10)

class TRANSACTION_TYPE(object):
    CONTRACT="ContractTransaction"
    CLAIM="ClaimTransaction"
    INVOKECONTRACT="InvocationTransaction"

localBlockCount = LocalBlockCout.query()
if localBlockCount:

    local_block_count=localBlockCount.height
else:
    local_block_count=0
    localBlockCount=LocalBlockCout.save(local_block_count)
while True:
    logger.info(local_block_count)
    block_h=BlockHeight.query()
    if not block_h:
        continue
    # try:
    #     redis_client.publish("monitor", json.dumps({"playload": block_h.height, "messageType": "monitorBlockHeight"}))
    # except Exception as e:
    #     logger.error("connect redis fail")
    if local_block_count<=block_h.height-1:
        exist_instance=Tx.query(local_block_count)
        if  exist_instance:
            for tx in exist_instance:
                tx_id=tx.tx_id
                tx_type=tx.tx_type
                block_height=tx.block_height
                block_time=tx.block_time
                vin=json.loads(tx.vin)
                vout=json.loads(tx.vout)


                #store contract tx
                if tx_type == TRANSACTION_TYPE.CONTRACT and len(vout) <=2:
                    asset_set=set()
                    for item in vout:
                        asset_set.add(item["asset"])
                    if len(asset_set)==1 and asset_set.pop() in [setting.NEO_ASSETID, setting.GAS_ASSETID]:
                        tmp_set=set()
                        address_from=None
                        for _vin in vin:
                            exist_instance = Vout.query(_vin["txid"], _vin["vout"])
                            if exist_instance:
                                tmp_set.add(exist_instance.address)
                                if len(tmp_set)==2:
                                    break
                                else:
                                    address_from=tmp_set.pop()


                        if address_from:
                            for _vout in vout:
                                if _vout["address"] == address_from:
                                    address_to=None
                                    value=None
                                    asset=None
                                    continue
                                address_to=_vout["address"]
                                value=_vout["value"]
                                asset=_vout["asset"]

                            if address_to and value and asset:
                                ContractTx.save(
                                    tx_id=tx_id, asset=asset, address_from=address_from, address_to=address_to,
                                    value=Decimal(str(value)), block_timestamp=block_time,
                                    block_height=block_height)

                                # try:
                                #     redis_client.publish("monitor",
                                #                          json.dumps({"playload": tx_id, "messageType": "monitorTx"}))
                                #
                                # except:
                                #     logger.error("connect redis fail")

                #store vout and calculate balance
                if vout:
                    for _vout in vout:
                        if _vout["asset"] in [setting.NEO_ASSETID, setting.GAS_ASSETID]:
                            saved = Vout.save(tx_id=tx_id, address=_vout["address"], asset_id=_vout["asset"],
                                         vout_number=_vout["n"], value=Decimal(_vout["value"]))
                            if not saved:
                                continue
                            exist_instance = Balance.query(address=_vout["address"])
                            if exist_instance:
                                if _vout["asset"]==setting.NEO_ASSETID:
                                    exist_instance.neo_balance += Decimal(_vout["value"])
                                else:
                                    exist_instance.gas_balance += Decimal(_vout["value"])
                                Balance.update(exist_instance)
                            else:
                                if _vout["asset"]==setting.NEO_ASSETID:
                                    new_instance = Balance(address=_vout["address"], neo_balance=Decimal(_vout["value"]))
                                else:
                                    new_instance = Balance(address=_vout["address"], gas_balance=Decimal(_vout["value"]))
                                Balance.save(new_instance)


                    for _vin in vin:
                        exist_instance = Vout.query(_vin["txid"],_vin["vout"])

                        if exist_instance:

                            Vout.delete(exist_instance)
                            balance_exist_instance = Balance.query(address=exist_instance.address)
                            if exist_instance.asset_id == setting.NEO_ASSETID:
                                balance_exist_instance.neo_balance -= Decimal(exist_instance.value)
                            else:
                                balance_exist_instance.gas_balance -= Decimal(exist_instance.value)
                            Balance.update(balance_exist_instance)
                        else:
                            logger.error("lost vout->tx_id:{},number:{}".format(_vin["txid"],_vin["vout"]))



                #store nep5 tx
                if tx_type != TRANSACTION_TYPE.INVOKECONTRACT:
                    continue


                content = get_application_log(tx_id)
                if not content:
                    continue
                if not content.get("notifications"):
                    continue
                for notification in content["notifications"]:
                    contract = notification["contract"]
                    if contract != setting.CONTRACTHASH:
                        continue
                    if bytearray.fromhex(notification["state"]["value"][0]["value"]).decode()!="transfer":
                        continue
                    address_from = hex2address(notification["state"]["value"][1]["value"])
                    address_to = hex2address(notification["state"]["value"][2]["value"])
                    value = hex2interger(notification["state"]["value"][3]["value"])
                    InvokeTx.save(
                        tx_id=tx_id, contract=contract, address_from=address_from, address_to=address_to,
                        value=Decimal(str(value)), vm_state=content["vmstate"], block_timestamp=block_time,
                        block_height=block_height)
                    # send to redis subpub
                    # try:
                    #     redis_client.publish("monitor", json.dumps({"playload": tx_id, "messageType": "monitorTx"}))
                    #
                    # except:
                    #     logger.error("connect redis fail")
        local_block_count+=1
        localBlockCount.height=local_block_count
        LocalBlockCout.update(localBlockCount)




    else:
        time.sleep(10)






