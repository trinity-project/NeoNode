import random
import time
import binascii
import requests
from neocore.Cryptography.Crypto import Crypto
from neocore.UInt160 import UInt160

from config import setting
from data_model.token_holding_model import BookmarkForTokenHolding,TokenHolding,Tx, BookmarkForBlock, logger



def hex2address(input):
    try:
        output = Crypto.ToAddress(UInt160(data=binascii.unhexlify(bytearray(input.encode("utf8")))))
    except:
        output = None
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
        except Exception as e:
            logger.error(e)
            time.sleep(10)


class TRANSACTION_TYPE(object):
    CONTRACT="ContractTransaction"
    CLAIM="ClaimTransaction"
    INVOKECONTRACT="InvocationTransaction"

#加载本地同步的快高
bookmarkForTokenHolding = BookmarkForTokenHolding.query()

if bookmarkForTokenHolding:
    bookmark_for_token_holding = bookmarkForTokenHolding.height
else:
    bookmark_for_token_holding = 0
    bookmarkForTokenHolding=BookmarkForTokenHolding.save(bookmark_for_token_holding)






def store_token_holding(executions):

        for execution in executions:
            if execution.get("vmstate") != "HALT, BREAK":
                continue
            for notification in execution.get("notifications"):
                contract = notification["contract"]
                try:
                    if bytearray.fromhex(notification["state"]["value"][0]["value"]).decode() != "transfer":
                        continue
                except:
                    continue
                address_to = hex2address(notification["state"]["value"][2]["value"])
                TokenHolding.save(contract=contract, address=address_to)

block_interval = 1000

while True:
    bookmark_for_block=BookmarkForBlock.query()
    logger.info("bookmark_token_holding:{} bookmark_block:{}".format(bookmark_for_token_holding,bookmark_for_block.height))
    if not bookmark_for_block:
        continue

    if bookmark_for_token_holding + block_interval > bookmark_for_block.height:
        block_interval = 0

    if bookmark_for_token_holding < bookmark_for_block.height:
        exist_instance=Tx.query(bookmark_for_token_holding,block_interval,TRANSACTION_TYPE.INVOKECONTRACT)
        if exist_instance:
            for tx in exist_instance:
                tx_id=tx.tx_id
                content = get_application_log(tx_id)

                if not content.get("executions"):
                    continue

                store_token_holding(content.get("executions"))

        # break
        bookmark_for_token_holding += block_interval + 1
        bookmarkForTokenHolding.height = bookmark_for_token_holding
        BookmarkForTokenHolding.update(bookmarkForTokenHolding)




    else:
        time.sleep(10)




