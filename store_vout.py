import json
import time
from data_model.vout_model import Tx, Vout, logger, HandledTx, Vin, BookmarkForBlock, BookmarkForVout, NeoTableSession

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


while True:
    bookmark_for_block=BookmarkForBlock.query()
    logger.info("bookmark_vout:{} bookmark_block:{}".format(bookmark_for_vout,bookmark_for_block.height))
    if not bookmark_for_block:
        continue



    if bookmark_for_vout<bookmark_for_block.height:
        exist_instance=Tx.query(bookmark_for_vout)
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
                    HandledTx.save(session,tx_id)
                    session.commit()
                except Exception as e:
                    session.rollback()
                    raise e
                finally:
                    session.close()

        bookmark_for_vout += 1
        bookmarkForVout.height = bookmark_for_vout
        BookmarkForVout.update(bookmarkForVout)




    else:
        time.sleep(10)




