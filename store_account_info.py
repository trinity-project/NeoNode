import json
import random
import time
import binascii
import requests
from decimal import Decimal
from neocore.Cryptography.Crypto import Crypto
from neocore.UInt160 import UInt160

from config import setting
from data_model.account_info_model import Tx, LocalBlockCout, Vout, Balance, \
    BlockHeight, logger, AccountInfoSession, HandledTx, Vin, ContractTx, InvokeTx


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
        except Exception as e:
            logger.error(e)
            time.sleep(10)


def push_event(to_push_message):
    while True:
        try:
            redis_client.publish("monitor", json.dumps( to_push_message))
            return True
        except Exception as e:
            logger.error("connect redis fail lead to push fail:{}".format(to_push_message))
            time.sleep(3)


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




def store_coin(session,tx_id,vin,vout):
    for _vout in vout:
        asset_id = _vout["asset"]
        address = _vout["address"]
        vout_number = _vout["n"]
        value = _vout["value"]

        Vout.save(session=session, tx_id=tx_id, address=address, asset_id=asset_id,
                  vout_number=vout_number, value=value)

    for _vin in vin:
        vin_txid = _vin["txid"]
        vin_vout_number = _vin["vout"]
        exist_vin = Vout.query(session,vin_txid, vin_vout_number)
        if exist_vin:
            Vout.delete(session, exist_vin)
            Vin.save(session, vin_txid, exist_vin.address, exist_vin.asset_id, vin_vout_number, exist_vin.value)
        else:
            raise Exception("lost vout->tx_id:{},number:{}".format(vin_txid, vin_vout_number))

def store_global_asset_tx(session,tx_id,vin,vout,block_height,block_time):
    address_from_asset_info = dict()
    address_to_asset_info = dict()

    for _vin in vin:
        vin_txid = _vin["txid"]
        vin_vout_number = _vin["vout"]
        vin_instance = Vin.query(session,vin_txid, vin_vout_number)

        if vin_instance:
            asset_mapping = address_from_asset_info.get(vin_instance.asset_id)
            if asset_mapping:
                address_amount = asset_mapping.get(vin_instance.address)
                if address_amount:
                    asset_mapping[vin_instance.address] = str(Decimal(address_amount) + Decimal(vin_instance.value))
                else:
                    asset_mapping[vin_instance.address] = vin_instance.value
            else:
                address_from_asset_info[vin_instance.asset_id] = {vin_instance.address: vin_instance.value}


        else:
            raise Exception("lost vin ({},{})".format(vin_txid, vin_vout_number))

    asset_mappings_of_from = list(address_from_asset_info.values())
    drop_tag = [True if len(am_of_from.keys()) >= 2 else False for am_of_from in asset_mappings_of_from]

    if True not in drop_tag:

        for _vout in vout:
            asset_id = _vout["asset"]
            address = _vout["address"]
            value = _vout["value"]

            asset_mapping = address_to_asset_info.get(asset_id)
            if asset_mapping:
                address_amount = asset_mapping.get(address)
                if address_amount:
                    asset_mapping[address] = str(Decimal(address_amount) + Decimal(value))
                else:
                    asset_mapping[address] = value
            else:
                address_to_asset_info[asset_id] = {address: value}

        for asset_type_from, address_mapping_from in address_from_asset_info.items():
            asset_type_from = asset_type_from
            address_from = list(address_mapping_from.keys())[0]

            for asset_type_to, address_mapping_to in address_to_asset_info.items():
                if asset_type_to == asset_type_from:
                    for address_to, amount in address_mapping_to.items():
                        address_to = address_to
                        amount = amount
                        if address_from != address_to:
                            ContractTx.save(session,tx_id,asset_type_to,address_from,address_to,amount,block_time,block_height)


def store_nep5_tx(session,tx_id):
    content = get_application_log(tx_id)
    if not content:
        return
    if not content.get("notifications"):
        return

    print(content.get("notifications"))
    for notification in content["notifications"]:
        print(notification)
        contract = notification["contract"]
        try:
            if bytearray.fromhex(notification["state"]["value"][0]["value"]).decode() != "transfer":
                continue
            address_from = hex2address(notification["state"]["value"][1]["value"])
            address_to = hex2address(notification["state"]["value"][2]["value"])
            value = hex2interger(notification["state"]["value"][3]["value"])
            # if contract == "0xfc732edee1efdf968c23c20a9628eaa5a6ccb934":
            #     value = value * (10 ** 6)
            InvokeTx.save(session=session,
                tx_id=tx_id, contract=contract, address_from=address_from, address_to=address_to,
                value=str(value), vm_state=content["vmstate"], block_timestamp=block_time,
                block_height=block_height)

            # push_event({"messageType": "monitorTx", "chainType": "NEO",
            #             "playload": tx_id, "blockNumber": local_block_count,
            #             "blockTimeStamp": block_time, "txId": tx_id})
            #
            # push_event({"messageType": "monitorAddress", "chainType": "NEO",
            #             "playload": address_to, "blockNumber": local_block_count,
            #             "blockTimeStamp": block_time, "addressFrom": address_from,
            #             "addressTo": address_to, "amount": str(value), "assetId": contract})

        except Exception as e:
            logger.error(e)


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

                session = AccountInfoSession(autocommit=True)

                handled_tx = HandledTx.query(session,tx_id)
                if handled_tx:
                    logger.info("tx {} has been handled".format(tx_id))
                    continue

                try:
                    session.begin(subtransactions=True)
                    store_coin(session,tx_id,vin,vout)
                    if tx_type == TRANSACTION_TYPE.CONTRACT:
                        store_global_asset_tx(session,tx_id,vin,vout,block_height,block_time)
                    # if tx_type == TRANSACTION_TYPE.INVOKECONTRACT:
                    #     store_nep5_tx(session,tx_id)


                    HandledTx.save(session,tx_id)
                    session.commit()
                except Exception as e:
                    logger.error(e)
                    session.rollback()
                finally:
                    session.close()
        # break
        local_block_count+=1
        localBlockCount.height=local_block_count
        LocalBlockCout.update(localBlockCount)




    else:
        time.sleep(10)




