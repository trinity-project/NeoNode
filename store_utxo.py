import json
import time


from data_model.utxo_model import Tx, Utxo,logger, HandledTx, BookmarkForBlock, BookmarkForUtxo, NeoTableSession

#加载本地同步的快高
bookmarkForUtxo = BookmarkForUtxo.query()

if bookmarkForUtxo:
    bookmark_for_utxo=bookmarkForUtxo.height
else:
    bookmark_for_utxo=0
    bookmarkForUtxo=BookmarkForUtxo.save(bookmark_for_utxo)



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
            Utxo.update(session, exist_utxo)
        else:
            raise Exception("lost utxo->tx_id:{},number:{}".format(vin_txid, vin_vout_number))



while True:
    bookmark_for_block=BookmarkForBlock.query()
    logger.info("bookmark_utxo:{} bookmark_block:{}".format(bookmark_for_utxo,bookmark_for_block.height))
    if not bookmark_for_block:
        continue



    if bookmark_for_utxo<bookmark_for_block.height:
        exist_instance=Tx.query(bookmark_for_utxo)
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
                    store_utxo(session,tx_id,vin,vout,bookmark_for_utxo)
                    HandledTx.save(session,tx_id)
                    session.commit()
                except Exception as e:
                    session.rollback()
                    raise e
                finally:
                    session.close()

        bookmark_for_utxo += 1
        bookmarkForUtxo.height = bookmark_for_utxo
        BookmarkForUtxo.update(bookmarkForUtxo)




    else:
        time.sleep(5)




