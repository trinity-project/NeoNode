import random
import time
import requests


from config import setting
from data_model.token_model import Tx, BookmarkForToken, BookmarkForBlock, Token ,logger



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



def get_token_info(tokenAddress):

    data = {
      "jsonrpc": "2.0",
      "method": "invokefunction",
      "id": 3
    }

    token_info = []

    try:
        for attr in ["name","symbol","decimals"]:
            data["params"] = [tokenAddress,attr,[]]
            res = requests.post(random.choice(setting.NEO_RPC_APPLICATION_LOG), json=data).json()
            value = res.get("result").get("stack")[0].get("value")
            if res.get("result").get("stack")[0].get("type") == "ByteArray":
                value = bytearray.fromhex(value).decode()
            token_info.append(value)

        return token_info
    except Exception as e:
        logger.error(e)
        return None



class TRANSACTION_TYPE(object):
    CONTRACT = "ContractTransaction"
    CLAIM = "ClaimTransaction"
    INVOKECONTRACT = "InvocationTransaction"


bookmarkForToken = BookmarkForToken.query()
if bookmarkForToken:

    bookmark_for_token = bookmarkForToken.height
else:
    bookmark_for_token = 0
    bookmarkForToken = BookmarkForToken.save(bookmark_for_token)
while True:
    logger.info(bookmark_for_token)
    bookmark_for_block = BookmarkForBlock.query()
    if not bookmark_for_block:
        continue
    if bookmark_for_token < bookmark_for_block.height:
        exist_instance = Tx.query(bookmark_for_token)
        if exist_instance:
            for tx in exist_instance:
                tx_id = tx.tx_id
                tx_type = tx.tx_type

                if tx_type != TRANSACTION_TYPE.INVOKECONTRACT:
                    continue

                content = get_application_log(tx_id)

                if not content.get("executions"):
                    continue

                for execution in content.get("executions"):
                    for notification in execution.get("notifications"):
                        contract = notification["contract"]
                        try:
                            if bytearray.fromhex(notification["state"]["value"][0]["value"]).decode() != "transfer":
                                continue

                            if Token.query_token(contract):
                                continue

                            token_info = get_token_info(contract)
                            if token_info:
                                logger.info("store token {}".format(contract))
                                Token.save(contract, token_info[0], token_info[1], token_info[2],
                                           "NEP-5", "NEO",
                                           )

                        except Exception as e:
                            logger.info(notification)
                            logger.error("contract address:{},error{}".format(contract, e))





        bookmark_for_token += 1
        bookmarkForToken.height = bookmark_for_token
        BookmarkForToken.update(bookmarkForToken)




    else:
        time.sleep(10)






