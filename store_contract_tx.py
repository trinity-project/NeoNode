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
from plugin.redis_client import redis_client


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
                if tx_type != TRANSACTION_TYPE.CONTRACT or len(vout) > 2 or len(vout) == 0:
                    continue


                asset_set=set()
                for item in vout:
                    asset_set.add(item["asset"])

                if len(asset_set) !=1 or asset_set.pop() not in [setting.NEO_ASSETID, setting.GAS_ASSETID]:
                    continue

                address_from_set=set()
                for _vin in vin:
                    exist_instance = Vout.query(_vin["txid"], _vin["vout"])
                    if exist_instance:
                        address_from_set.add(exist_instance.address)

                if address_from_set !=1:
                    continue

                address_from=address_from_set.pop()
                address_to = None
                value = None
                asset = None

                for _vout in vout:
                    if _vout["address"] != address_from:

                        address_to=_vout["address"]
                        value=_vout["value"]
                        asset=_vout["asset"]

                if address_to and value and asset:
                    ContractTx.save(
                        tx_id=tx_id, asset=asset, address_from=address_from, address_to=address_to,
                        value=Decimal(str(value)), block_timestamp=block_time,
                        block_height=block_height)



        local_block_count+=1
        localBlockCount.height=local_block_count
        LocalBlockCout.update(localBlockCount)




    else:
        time.sleep(10)






