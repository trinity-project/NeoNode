#!/usr/bin/env python
# coding=utf-8
import binascii
import requests
import json
import time
from decimal import Decimal
from neocore.Cryptography.Crypto import Crypto
from neocore.UInt160 import UInt160
from config import setting
from data_model.account_info_model import Tx,LocalBlockCout,BlockHeight,InvokeTx
from project_log import setup_mylogger

logger=setup_mylogger()



class TRANSACTION_TYPE(object):
    CONTRACT="ContractTransaction"
    CLAIM="ClaimTransaction"
    INVOKECONTRACT="InvocationTransaction"

def hex_reverse(input):
    tmp_list = []
    for i in range(0, len(input), 2):
        tmp_list.append(input[i:i + 2])
    hex_str = "".join(list(reversed(tmp_list)))
    return hex_str

def hex2address(input):
    output = Crypto.ToAddress(UInt160(data=binascii.unhexlify(bytearray(input.encode("utf8")))))


    return output

def hex2interger(input):
    tmp_list = []
    for i in range(0, len(input), 2):
        tmp_list.append(input[i:i + 2])
    hex_str = "".join(list(reversed(tmp_list)))
    output = int(hex_str, 16) / 100000000

    return output

def get_application_log(txid,retry_num=3):

    data = {
          "jsonrpc": "2.0",
          "method": "getapplicationlog",
          "params": [txid],
          "id": 1
}


    try:
        res = requests.post(setting.NEOCLIURL,json=data).json()
        return res["result"]
    except Exception as e:
        retry_num-=1
        if retry_num==0:
            logger.error("txid:{} get application log   fail \n {}".format(txid, e))
            return None
        return get_application_log(txid,retry_num)




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

    if local_block_count<=block_h.height:
        exist_instance=Tx.query(local_block_count)
        if  exist_instance:
            for tx in exist_instance:
                tx_type=tx.tx_type
                if tx_type != TRANSACTION_TYPE.INVOKECONTRACT:
                    continue
                tx_id=tx.tx_id
                block_height=tx.block_height
                block_time=tx.block_time

                content = json.loads(get_application_log(tx_id))
                if not content["notifications"]:
                    continue
                for notification in content["notifications"]:
                    contract = notification["contract"]
                    if contract != setting.CONTRACTHASH:
                        continue
                    address_from = hex2address(notification["state"]["value"][1]["value"])
                    address_to = hex2address(notification["state"]["value"][2]["value"])
                    value = hex2interger(notification["state"]["value"][3]["value"])
                    InvokeTx.save(
                        tx_id=tx_id, contract=contract, address_from=address_from, address_to=address_to,
                        value=Decimal(str(value)), vm_state=content["vmstate"], block_timestamp=block_time,
                        block_height=block_height)

        local_block_count+=1
        localBlockCount.height=local_block_count
        LocalBlockCout.update(localBlockCount)




    else:
        time.sleep(15)






