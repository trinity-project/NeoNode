
import json
import random

import requests
import time


from config import setting
from data_model.block_info_model import Tx,logger





def getblock(index,retry_num=3):

    data = {
          "jsonrpc": "2.0",
          "method": "getblock",
          "params": [index,1],
          "id": 1
}


    try:
        res = requests.post(random.choice(setting.NEOCLIURL),json=data).json()
        return res["result"]
    except Exception as e:
        retry_num-=1
        if retry_num==0:
            return None
        return getblock(index,retry_num)



bookmark_for_block=0



while True:
    logger.info(bookmark_for_block)
    block_info=getblock(bookmark_for_block)
    if not block_info:

        time.sleep(5)
        continue

    tx = block_info["tx"][0]



    if tx["vout"]:
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

    bookmark_for_block+=1





