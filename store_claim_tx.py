import json
import time

from data_model.claim_model import   Tx, ClaimTx, BookmarkForBlock, BookmarkForClaim, logger, NeoTableSession




class TRANSACTION_TYPE(object):
    CONTRACT="ContractTransaction"
    CLAIM="ClaimTransaction"
    INVOKECONTRACT="InvocationTransaction"

#加载本地同步的快高
bookmarkForClaim = BookmarkForClaim.query()

if bookmarkForClaim:
    bookmark_for_claim = bookmarkForClaim.height
else:
    bookmark_for_claim = 0
    bookmarkForClaim=BookmarkForClaim.save(bookmark_for_claim)



def store_claim_tx(session,tx_id,block_time,vout):
    for item in vout:
        address_to = item.get("address")
        value = item.get("value")
        ClaimTx.save(session,tx_id,address_to,value,block_time)

block_interval = 1000

while True:
    bookmark_for_block=BookmarkForBlock.query()
    logger.info("bookmark_claim_tx:{} bookmark_block:{}".format(bookmark_for_claim,bookmark_for_block.height))
    if not bookmark_for_block:
        time.sleep(10)
        continue

    if bookmark_for_claim + block_interval > bookmark_for_block.height:
        block_interval = 0

    if bookmark_for_claim <= bookmark_for_block.height:
        exist_instance=Tx.query(bookmark_for_claim,block_interval,TRANSACTION_TYPE.CLAIM)
        logger.info(len(exist_instance))
        if exist_instance:
            for tx in exist_instance:
                tx_id=tx.tx_id
                logger.info(tx_id)
                tx_type=tx.tx_type
                block_time=tx.block_time
                vout=json.loads(tx.vout)

                session = NeoTableSession(autocommit=True)
                try:
                    session.begin(subtransactions=True)
                    store_claim_tx(session,tx_id,block_time,vout)
                    session.commit()
                except Exception as e:
                    session.rollback()
                    raise e
                finally:
                    session.close()
        # break
        bookmark_for_claim += block_interval + 1
        bookmarkForClaim.height = bookmark_for_claim
        BookmarkForClaim.update(bookmarkForClaim)




    else:
        time.sleep(10)




