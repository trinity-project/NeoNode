
import json
import requests
import time


from config import setting
from data_model.block_info_model import LocalBlockCout,Tx,logger




class TRANSACTION_TYPE(object):
    CONTRACT="ContractTransaction"
    CLAIM="ClaimTransaction"
    INVOKECONTRACT="InvocationTransaction"
    ISSUE="IssueTransaction"


def getblock(index,retry_num=3):

    data = {
          "jsonrpc": "2.0",
          "method": "getblock",
          "params": [index,1],
          "id": 1
}


    try:
        res = requests.post(setting.NEOCLIURL,json=data).json()
        return res["result"]
    except Exception as e:
        retry_num-=1
        if retry_num==0:
            return None
        return getblock(index,retry_num)


localBlockCount = LocalBlockCout.query()
if localBlockCount:

    local_block_count=localBlockCount.height
else:
    local_block_count=0
    localBlockCount=LocalBlockCout.save(local_block_count)


while True:
    logger.info(local_block_count)
    block_info=getblock(local_block_count)
    if not block_info:

        time.sleep(5)
        continue
    if len(block_info["tx"])>1:
        for tx in block_info["tx"][1:]:
            tx_type=tx["type"]
            tx_id=tx["txid"]
            block_height=block_info["index"]
            block_time=block_info["time"]
            vin=json.dumps(tx["vin"])
            vout=json.dumps(tx["vout"])
            scripts=""
            attributes=json.dumps(tx["attributes"])
            script=tx.get("script")
            Tx.save(tx_id,tx_type,block_height,block_time,vin,vout,script)

    else:
        if block_info["tx"][0]["vout"]:
            tx_type=tx["type"]
            tx_id=tx["txid"]
            block_height=block_info["index"]
            block_time=block_info["time"]
            vin=json.dumps(tx["vin"])
            vout=json.dumps(tx["vout"])
            scripts=""
            attributes=json.dumps(tx["attributes"])
            script=tx.get("script")
            Tx.save(tx_id,tx_type,block_height,block_time,vin,vout,script)

    local_block_count+=1
    localBlockCount.height=local_block_count
    LocalBlockCout.update(localBlockCount)




