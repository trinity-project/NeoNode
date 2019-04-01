import json
import time

from sqlalchemy.orm import sessionmaker

from data_model.block_info_model import engine, Tx
from data_model.claim_model import ClaimTx, BookmarkForClaim, neo_table_engine
from data_model.utxo_model import Utxo, BookmarkForUtxo
from project_log.my_log import setup_logger
from utils.utils import TRANSACTION_TYPE


def store_claim_tx(session,tx_id,block_time,vout,claims):
    for item in vout:
        address_to = item.get("address")
        value = item.get("value")
        ClaimTx.save(session,tx_id,address_to,value,block_time,json.dumps(claims))


def update_utxo_status(session,claims):
    for item in claims:
        exist_instance = Utxo.query(session,item.get("txid"),str(item.get("vout")))
        exist_instance.is_claimed = True
        Utxo.update(session,exist_instance)




if __name__ == "__main__":
    logger = setup_logger()

    BlockInfoSession = sessionmaker(bind=engine)
    NeoTableSession = sessionmaker(bind=neo_table_engine)

    neo_table_session = NeoTableSession()


    # 加载本地同步的快高
    bookmarkForClaim = BookmarkForClaim.query(neo_table_session)

    if bookmarkForClaim:
        bookmark_for_claim = bookmarkForClaim.height
    else:
        bookmark_for_claim = -1
        bookmarkForClaim = BookmarkForClaim.save(neo_table_session,bookmark_for_claim)

    block_interval = 1000
    while True:



        bookmark_for_claim += 1
        bookmarkForUtxo=BookmarkForUtxo.query(neo_table_session)

        bookmark_for_utxo = bookmarkForUtxo.height
        if bookmark_for_claim + block_interval > bookmark_for_utxo:
            block_interval = 0

        if bookmark_for_claim <= bookmark_for_utxo:
            block_info_session = BlockInfoSession()
            exist_instance = block_info_session.query(Tx).filter(Tx.block_height >= bookmark_for_claim,
                                                                 Tx.block_height <= bookmark_for_claim + block_interval,
                                                                 Tx.tx_type == TRANSACTION_TYPE.CLAIM).all()
            if exist_instance:
                for tx in exist_instance:
                    tx_id=tx.tx_id
                    tx_type=tx.tx_type
                    block_time=tx.block_time
                    vout=json.loads(tx.vout)
                    claims=json.loads(tx.claims)

                    store_claim_tx(neo_table_session,tx_id,block_time,vout,claims)
                    update_utxo_status(neo_table_session,claims)


            bookmarkForClaim.height = bookmark_for_claim
            BookmarkForClaim.update(neo_table_session,bookmarkForClaim)
            try:
                neo_table_session.commit()
            except Exception as e:
                neo_table_session.rollback()
                raise e


            logger.info("bookmark_claim_tx:{} bookmark_utxo:{}".format(bookmark_for_claim, bookmark_for_utxo))




        else:
            bookmark_for_claim -= 1
            time.sleep(3)




