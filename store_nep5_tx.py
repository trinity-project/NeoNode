import json
import random
import time
import binascii
import requests
from decimal import Decimal

import sqlalchemy
from neocore.Cryptography.Crypto import Crypto
from neocore.UInt160 import UInt160

from config import setting
from data_model.nep5_model import Tx, InvokeTx, BookmarkForBlock, BookmarkForNep5, logger, NeoTableSession
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
    except:
        output = None
    return output

def hex2interger(input):
    try:
        tmp_list = []
        for i in range(0, len(input), 2):
            tmp_list.append(input[i:i + 2])
        hex_str = "".join(list(reversed(tmp_list)))
        output = int(hex_str, 16)

        return output
    except:
        return None

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


def md5_for_invoke_tx(tx_id,address_from,address_to,value,contract):
    import hashlib
    src = "{}{}{}{}{}".format(tx_id,address_from,address_to,value,contract).encode()
    m1 = hashlib.md5()
    m1.update(src)
    return m1.hexdigest()


# def push_event(to_push_message):
#     while True:
#         try:
#             redis_client.publish("monitor", json.dumps( to_push_message))
#             return True
#         except Exception as e:
#             logger.error("connect redis fail lead to push fail:{}".format(to_push_message))
#             time.sleep(3)


class TRANSACTION_TYPE(object):
    CONTRACT="ContractTransaction"
    CLAIM="ClaimTransaction"
    INVOKECONTRACT="InvocationTransaction"

#加载本地同步的快高
bookmarkForNep5 = BookmarkForNep5.query()

if bookmarkForNep5:
    bookmark_for_nep5 = bookmarkForNep5.height
else:
    bookmark_for_nep5 = 0
    bookmarkForNep5=BookmarkForNep5.save(bookmark_for_nep5)






def store_nep5_tx(executions,txid,block_height,block_time):
    session = NeoTableSession(autocommit=True)
    try:
        session.begin(subtransactions=True)
        for execution in executions:
            for notification in execution.get("notifications"):
                contract = notification["contract"]
                try:
                    if bytearray.fromhex(notification["state"]["value"][0]["value"]).decode() != "transfer":
                        continue
                except:
                    continue
                address_from = hex2address(notification["state"]["value"][1]["value"])
                address_to = hex2address(notification["state"]["value"][2]["value"])
                value = hex2interger(notification["state"]["value"][3]["value"]) if notification["state"]["value"][3]["type"] != "Integer"\
                    else notification["state"]["value"][3]["value"]
                md5_of_tx = md5_for_invoke_tx(tx_id,address_from,address_to,value,contract)

                if address_from and address_to and value:

                    InvokeTx.save(session=session,
                                  tx_id=txid, contract=contract, address_from=address_from, address_to=address_to,
                                  value=str(value), vm_state=execution["vmstate"], block_timestamp=block_time,
                                  block_height=block_height,md5_of_tx=md5_of_tx)

                # push_event({"messageType": "monitorTx", "chainType": "NEO",
                #             "playload": tx_id, "blockNumber": local_block_count,
                #             "blockTimeStamp": block_time, "txId": tx_id})
                #
                # push_event({"messageType": "monitorAddress", "chainType": "NEO",
                #             "playload": address_to, "blockNumber": local_block_count,
                #             "blockTimeStamp": block_time, "addressFrom": address_from,
                #             "addressTo": address_to, "amount": str(value), "assetId": contract})
        session.commit()
    except sqlalchemy.exc.IntegrityError as e:
        session.rollback()
        logger.error(e)
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()

block_interval = 0

while True:
    bookmark_for_block=BookmarkForBlock.query()
    logger.info("bookmark_nep5:{} bookmark_block:{}".format(bookmark_for_nep5,bookmark_for_block.height))
    if not bookmark_for_block:
        continue

    if bookmark_for_nep5 + block_interval > bookmark_for_block.height:
        block_interval = 0

    if bookmark_for_nep5 < bookmark_for_block.height:
        exist_instance=Tx.query(bookmark_for_nep5,block_interval,TRANSACTION_TYPE.INVOKECONTRACT)
        if exist_instance:
            for tx in exist_instance:
                tx_id=tx.tx_id
                tx_type=tx.tx_type
                block_height=tx.block_height
                block_time=tx.block_time
                vin=json.loads(tx.vin)
                vout=json.loads(tx.vout)

                if tx_type != TRANSACTION_TYPE.INVOKECONTRACT:
                    continue

                content = get_application_log(tx_id)

                if not content.get("executions"):
                    continue

                store_nep5_tx(content.get("executions"),content.get("txid"),block_height,block_time)

        # break
        bookmark_for_nep5 += block_interval + 1
        bookmarkForNep5.height = bookmark_for_nep5
        BookmarkForNep5.update(bookmarkForNep5)




    else:
        time.sleep(10)




