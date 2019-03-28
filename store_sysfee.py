import time
from decimal import Decimal

from data_model.block_info_model import BlockInfoSession, BookmarkForBlock, Tx
from data_model.sysfee_model import  Sysfee, BookmarkForSysfee, NeoTableSession

from project_log import setup_logger


def store_sysfee(session,block_height,sys_fee):

    exist_instance = Sysfee.query(session,block_height-1)
    if exist_instance:
        pre_sysfee = exist_instance.sys_fee
        Sysfee.save(session,block_height,str(sys_fee + Decimal(pre_sysfee)))
    else:
        Sysfee.save(session, block_height, str(sys_fee))


if __name__ == "__main__":
    logger = setup_logger()
    sys_fee_session = NeoTableSession()
    block_info_session = BlockInfoSession()

    bookmarkForSysfee = BookmarkForSysfee.query(sys_fee_session)
    if bookmarkForSysfee:
        bookmark_for_sysfee = bookmarkForSysfee.height
    else:
        bookmark_for_sysfee = -1


    while True:
        bookmark_for_sysfee += 1
        bookmark_for_block=BookmarkForBlock.query(BlockInfoSession)

        if bookmark_for_sysfee <= bookmark_for_block.height:
            exist_instance=Tx.query(block_info_session,bookmark_for_sysfee)
            if exist_instance:
                sys_fee = Decimal(0)
                for tx in exist_instance:
                    # net_fee = Decimal(tx.net_fee)
                    sys_fee += Decimal(tx.sys_fee)


                store_sysfee(sys_fee_session,bookmark_for_sysfee,sys_fee)


            bookmarkForSysfee.height = bookmark_for_sysfee
            BookmarkForSysfee.update(sys_fee_session,bookmarkForSysfee)
            try:
                sys_fee_session.commit()
            except Exception as e:
                sys_fee_session.rollback()
                raise e
            finally:
                sys_fee_session.close()
            logger.info("bookmark_sysfee:{} bookmark_block:{}".format(bookmark_for_sysfee, bookmark_for_block.height))




        else:
            time.sleep(3)




