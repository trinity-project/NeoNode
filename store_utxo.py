import json
import time
from decimal import Decimal

from sqlalchemy.orm import sessionmaker

from config import setting
from data_model.utxo_model import Utxo, BookmarkForUtxo, neo_table_engine
from data_model.sysfee_model import BookmarkForSysfee,Sysfee
from data_model.block_info_model import Tx, engine
from project_log import setup_logger


#以1个NEO计算
def count_block_reward_gas(start_block,end_block):
    step = 2000000
    block_reward = 8
    gas_count = 0
    for i in range(22):
        start = i * step
        end = (i+1) * step -1
        if end_block < start:
            break
        if start_block <= end:
            if start_block > start:
                start = start_block
            if end_block < end:
                end = end_block
            gas_count += (end - start) * block_reward

        if block_reward > 1:
            block_reward -= 1
    return Decimal(gas_count)/pow(10,8)

#以1个NEO计算
def count_sysfee_gas(session,start_block,end_block):
    total_sysfee_start = Sysfee.query(session,start_block)
    total_sysfee_end = Sysfee.query(session,end_block)
    diffence_fee = Decimal(total_sysfee_end.sys_fee) - Decimal(total_sysfee_start.sys_fee)
    return diffence_fee/pow(10,8)

#存储零花钱
def store_utxo(session,tx_id,vin,vout,block_height):

    for _vout in vout:
        asset_id = _vout["asset"]
        address = _vout["address"]
        vout_number = _vout["n"]
        value = _vout["value"]

        Utxo.save(session=session, tx_id=tx_id, address=address, asset_id=asset_id,
                  vout_number=vout_number, value=value,start_block=block_height)

    for _vin in vin:
        vin_txid = _vin["txid"]
        vin_vout_number = _vin["vout"]
        exist_utxo = Utxo.query(session,vin_txid, vin_vout_number)
        if exist_utxo:
            exist_utxo.end_block = block_height
            exist_utxo.is_used = True
            if exist_utxo.asset_id == setting.NEO_ASSETID:
                gas_reward = count_block_reward_gas(start_block=exist_utxo.start_block,end_block=block_height)
                gas_sysfee = count_sysfee_gas(session=session,start_block=exist_utxo.start_block,end_block=block_height)
                gen_gas = str((gas_reward + gas_sysfee) * Decimal(exist_utxo.value))
                exist_utxo.gen_gas = gen_gas

            Utxo.update(session, exist_utxo)
        else:
            raise Exception("lost utxo->tx_id:{},number:{}".format(vin_txid, vin_vout_number))




if __name__ == "__main__":

    logger = setup_logger()

    BlockInfoSession = sessionmaker(bind=engine)
    NeoTableSession = sessionmaker(bind=neo_table_engine)

    neo_table_session = NeoTableSession()


    # 加载本地同步的快高
    bookmarkForUtxo = BookmarkForUtxo.query(neo_table_session)

    if bookmarkForUtxo:
        bookmark_for_utxo = bookmarkForUtxo.height
    else:
        bookmark_for_utxo = -1
        bookmarkForUtxo = BookmarkForUtxo.save(neo_table_session,bookmark_for_utxo)


    while True:

        bookmark_for_utxo += 1

        block_info_session = BlockInfoSession()
        bookmarkForSysfee=BookmarkForSysfee.query(neo_table_session)
        bookmark_for_sysfee = bookmarkForSysfee.height

        if bookmark_for_utxo <= bookmark_for_sysfee:
            exist_instance = block_info_session.query(Tx).filter(Tx.block_height == bookmark_for_utxo).all()
            if  exist_instance:
                for tx in exist_instance:
                    tx_id=tx.tx_id
                    tx_type=tx.tx_type
                    block_height=tx.block_height
                    block_time=tx.block_time
                    vin=json.loads(tx.vin)
                    vout=json.loads(tx.vout)

                    store_utxo(neo_table_session,tx_id,vin,vout,bookmark_for_utxo)



            bookmarkForUtxo.height = bookmark_for_utxo
            BookmarkForUtxo.update(neo_table_session,bookmarkForUtxo)

            try:
                neo_table_session.commit()
            except Exception as e:
                neo_table_session.rollback()
                raise e


            logger.info("bookmark_utxo:{} bookmark_sysfee:{}".format(bookmark_for_utxo, bookmark_for_sysfee))

        else:
            bookmark_for_utxo -= 1
            time.sleep(3)


        block_info_session.close()

