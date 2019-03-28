
import json
import random

import requests
import time


from config import setting
from data_model.block_info_model import BookmarkForBlock,Tx,logger





def getblock(index):

    data = {
          "jsonrpc": "2.0",
          "method": "getblock",
          "params": [index,1],
          "id": 1
}


    try:
        res = requests.post(random.choice(setting.NEOCLIURL),json=data).json()
        return res["result"]
    except:
        return None


bookmarkForBlock = BookmarkForBlock.query()
if bookmarkForBlock:

    bookmark_for_block=bookmarkForBlock.height
else:
    bookmark_for_block=0
    bookmarkForBlock=BookmarkForBlock.save(bookmark_for_block)


while True:
    logger.info(bookmark_for_block)
    block_info=getblock(bookmark_for_block)
    if not block_info:

        time.sleep(5)
        continue
    for tx in block_info["tx"]:
        tx_type=tx["type"]
        tx_id=tx["txid"]
        block_height=block_info["index"]
        block_time=block_info["time"]
        vin=json.dumps(tx["vin"])
        vout=json.dumps(tx["vout"])
        sys_fee = tx["sys_fee"]
        net_fee = tx["net_fee"]
        claims = json.dumps(tx.get("claims",[]))
        Tx.save(tx_id,tx_type,block_height,block_time,vin,vout,sys_fee,net_fee,claims=claims)



    bookmark_for_block+=1
    bookmarkForBlock.height=bookmark_for_block
    BookmarkForBlock.update(bookmarkForBlock)




