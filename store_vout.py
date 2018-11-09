import json
import time

from decimal import Decimal

from data_model.vout_model import Tx, Vout, logger, HandledTx, Vin, BookmarkForBlock, BookmarkForVout, NeoTableSession, \
    ContractTx

#加载本地同步的快高
bookmarkForVout = BookmarkForVout.query()

if bookmarkForVout:
    bookmark_for_vout=bookmarkForVout.height
else:
    bookmark_for_vout=0
    bookmarkForVout=BookmarkForVout.save(bookmark_for_vout)



#存储零花钱
def store_vout(session,tx_id,vin,vout):
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

#存储全局资产交易记录
def store_contract_tx(session,tx_id,vin,vout,block_height,block_time):

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


block_interval = 1000

while True:
    bookmark_for_block=BookmarkForBlock.query()
    logger.info("bookmark_vout:{} bookmark_block:{}".format(bookmark_for_vout,bookmark_for_block.height))
    if not bookmark_for_block:
        continue

    if bookmark_for_vout + block_interval > bookmark_for_block.height:
        block_interval = 0

    if bookmark_for_vout<=bookmark_for_block.height:
        exist_instance=Tx.query(bookmark_for_vout,block_interval)
        if  exist_instance:
            for tx in exist_instance:
                tx_id=tx.tx_id
                tx_type=tx.tx_type
                block_height=tx.block_height
                block_time=tx.block_time
                vin=json.loads(tx.vin)
                vout=json.loads(tx.vout)

                session = NeoTableSession(autocommit=True)

                handled_tx = HandledTx.query(session,tx_id)
                if handled_tx:
                    logger.info("tx {} has been handled".format(tx_id))
                    continue

                try:
                    session.begin(subtransactions=True)
                    store_vout(session,tx_id,vin,vout)
                    store_contract_tx(session, tx_id, vin, vout, block_height, block_time)
                    HandledTx.save(session,tx_id)
                    session.commit()
                except Exception as e:
                    session.rollback()
                    raise e
                finally:
                    session.close()

        bookmark_for_vout += block_interval +1
        bookmarkForVout.height = bookmark_for_vout
        BookmarkForVout.update(bookmarkForVout)




    else:
        time.sleep(10)




