import json
import time

from decimal import Decimal

from data_model.utxo_model import Tx, Utxo,logger, HandledTx, BookmarkForSysfee, BookmarkForUtxo, NeoTableSession,Sysfee


NEO_ASSETID = "0xc56f33fc6ecfcd0c225c4ab356fee59390af8560be0e930faebe74a6daff7c9b"

#加载本地同步的快高
bookmarkForUtxo = BookmarkForUtxo.query()

if bookmarkForUtxo:
    bookmark_for_utxo=bookmarkForUtxo.height
else:
    bookmark_for_utxo=-1
    bookmarkForUtxo=BookmarkForUtxo.save(bookmark_for_utxo)


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
def count_sysfee_gas(start_block,end_block):
    total_sysfee_start = Sysfee.query(start_block)
    total_sysfee_end = Sysfee.query(end_block)
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
            if exist_utxo.asset_id == NEO_ASSETID:
                gas_reward = count_block_reward_gas(start_block=exist_utxo.start_block,end_block=block_height)
                gas_sysfee = count_sysfee_gas(start_block=exist_utxo.start_block,end_block=block_height)
                gen_gas = str((gas_reward + gas_sysfee) * Decimal(exist_utxo.value))
                exist_utxo.gen_gas = gen_gas
                logger.info("txid:{} vout_number:{}  gen_gas:{} reward:{} sys:{}".format(
                                                                                exist_utxo.tx_id,
                                                                              exist_utxo.vout_number,
                                                                              exist_utxo.gen_gas,
                                                                              str(gas_reward  * Decimal(exist_utxo.value)),
                                                                              str(gas_sysfee * Decimal(exist_utxo.value))
                                                                              ))
            Utxo.update(session, exist_utxo)
        else:
            raise Exception("lost utxo->tx_id:{},number:{}".format(vin_txid, vin_vout_number))



while True:
    bookmark_for_utxo += 1
    bookmark_for_sysfee=BookmarkForSysfee.query()

    session = NeoTableSession(autocommit=True)
    session.begin(subtransactions=True)

    if bookmark_for_utxo <= bookmark_for_sysfee.height:
        exist_instance=Tx.query(bookmark_for_utxo)
        if  exist_instance:
            for tx in exist_instance:
                tx_id=tx.tx_id
                tx_type=tx.tx_type
                block_height=tx.block_height
                block_time=tx.block_time
                vin=json.loads(tx.vin)
                vout=json.loads(tx.vout)



                # handled_tx = HandledTx.query(session,tx_id)
                # if handled_tx:
                #     logger.info("tx {} has been handled".format(tx_id))
                #     continue

                try:

                    store_utxo(session,tx_id,vin,vout,bookmark_for_utxo)
                    HandledTx.save(session,tx_id)
                    session.commit()
                except Exception as e:
                    session.rollback()
                    raise e
                finally:
                    session.close()

        
        bookmarkForUtxo.height = bookmark_for_utxo
        BookmarkForUtxo.update(bookmarkForUtxo)
        logger.info("bookmark_utxo:{} bookmark_sysfee:{}".format(bookmark_for_utxo, bookmark_for_sysfee.height))

    else:
        time.sleep(3)




