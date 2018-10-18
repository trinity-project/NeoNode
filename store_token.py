import json
import random
import time
import binascii
import requests
from decimal import Decimal
from neocore.Cryptography.Crypto import Crypto
from neocore.UInt160 import UInt160

from config import setting
from data_model.model import Tx, LocalBlockCout, BlockHeight, Token ,logger



def get_application_log(txid):
    data = {
        "jsonrpc": "2.0",
        "method": "getapplicationlog",
        "params": [txid],
        "id": 1
    }

    try:
        res = requests.post(random.choice(setting.NEO_RPC_APPLICATION_LOG), json=data).json()
        if res.get("result"):
            return res.get("result")
    except Exception as e:
        logger.error(e)



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


localBlockCount = LocalBlockCout.query()
if localBlockCount:

    local_block_count = localBlockCount.height
else:
    local_block_count = 0
    localBlockCount = LocalBlockCout.save(local_block_count)
while True:
    logger.info(local_block_count)
    block_h = BlockHeight.query()
    if not block_h:
        continue
    if local_block_count <= block_h.height - 1:
        exist_instance = Tx.query(local_block_count)
        if exist_instance:
            for tx in exist_instance:
                tx_id = tx.tx_id
                tx_type = tx.tx_type

                # store nep5 tx
                if tx_type != TRANSACTION_TYPE.INVOKECONTRACT:
                    continue

                content = get_application_log(tx_id)
                if not content:
                    continue
                if not content.get("notifications"):
                    continue
                for notification in content["notifications"]:
                    contract = notification["contract"]
                    try:
                        if bytearray.fromhex(notification["state"]["value"][0]["value"]).decode() != "transfer":
                            continue

                        if Token.query_token(contract):
                            continue

                        token_info = get_token_info(contract)
                        if token_info:

                            Token.save(contract,token_info[0],token_info[1],token_info[2],
                                       "NEP-5","NEO","https://appserver.trinity.ink/static/icon/{}.png".format(token_info[1]))

                    except Exception as e:
                        logger.info(notification)
                        logger.info(token_info)
                        logger.error("contract address:{},error{}".format(contract,e))

        local_block_count += 1
        localBlockCount.height = local_block_count
        LocalBlockCout.update(localBlockCount)




    else:
        time.sleep(10)






