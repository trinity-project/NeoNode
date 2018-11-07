import json
import random
import time
import binascii
import requests
from decimal import Decimal
from neocore.Cryptography.Crypto import Crypto
from neocore.UInt160 import UInt160

from config import setting
from data_model.account_info_model import Tx, LocalBlockCout,  BlockHeight,logger,Vin





class TRANSACTION_TYPE(object):
    CONTRACT="ContractTransaction"
    CLAIM="ClaimTransaction"
    INVOKECONTRACT="InvocationTransaction"

local_block_count = 6798


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




                if tx_type != TRANSACTION_TYPE.CONTRACT:
                    continue

                address_from_asset_info=dict()
                address_to_asset_info=dict()

                for _vin in vin:
                    vin_txid = _vin["txid"]
                    vin_vout_number = _vin["vout"]
                    vin_instance = Vin.query(vin_txid,vin_vout_number)

                    if vin_instance:
                        asset_mapping = address_from_asset_info.get(vin_instance.asset_id)
                        if asset_mapping:
                            address_amount = asset_mapping.get(vin_instance.address)
                            if address_amount:
                                asset_mapping[vin_instance.address] = str(Decimal(address_amount) + Decimal(vin_instance.value))
                            else:
                                asset_mapping[vin_instance.address] = vin_instance.value
                        else:
                            address_from_asset_info[vin_instance.asset_id] = {vin_instance.address:vin_instance.value}


                    else:
                        logger.info("lost vin ({},{})".format(vin_txid,vin_vout_number))



                asset_mappings_of_from = list(address_from_asset_info.values())
                drop_tag = [True if len(am_of_from.keys()) >=2 else False for am_of_from in asset_mappings_of_from ]

                if True in drop_tag:
                    continue

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


                asset_mappings_of_to = address_to_asset_info.values()

                for asset_type_from,address_mapping_from in address_from_asset_info.items():
                    asset_type_from = asset_type_from
                    address_from = list(address_mapping_from.keys())[0]

                    for asset_type_to, address_mapping_to in address_to_asset_info.items():
                        if asset_type_to == asset_type_from:
                            for address_to,amount in address_mapping_to.items():
                                address_to = address_to
                                amount = amount
                                if address_from != address_to:
                                    logger.info("addressFrom:{},addressTo:{},amount:{},asset:{}".format(address_from,address_to,amount,asset_type_to))


        local_block_count+=1
        # break
        # localBlockCount.height=local_block_count
        # LocalBlockCout.update(localBlockCount)




    else:
        time.sleep(10)




