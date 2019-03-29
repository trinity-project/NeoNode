import time
from decimal import Decimal

from sqlalchemy.orm import sessionmaker

from data_model.block_info_model import BookmarkForBlock, Tx, engine
from data_model.sysfee_model import Sysfee, BookmarkForSysfee, neo_table_engine

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

    NeoTableSession = sessionmaker(bind=neo_table_engine)
    BlockInfoSession = sessionmaker(bind=engine)
    sys_fee_session = NeoTableSession()


    bookmarkForSysfee = BookmarkForSysfee.query(sys_fee_session)
    if bookmarkForSysfee:
        bookmark_for_sysfee = bookmarkForSysfee.height
    else:
        bookmark_for_sysfee = -1
        bookmarkForSysfee = BookmarkForSysfee.save(sys_fee_session,bookmark_for_sysfee)


    while True:
        bookmark_for_sysfee += 1
        block_info_session = BlockInfoSession()
        bookmarkForBlock=BookmarkForBlock.query(block_info_session)
        bookmark_for_block = bookmarkForBlock.height
        if bookmark_for_sysfee <= bookmark_for_block:
            exist_instance = block_info_session.query(Tx).filter(Tx.block_height==bookmark_for_sysfee).all()
            block_info_session.close()
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
            logger.info("bookmark_sysfee:{} bookmark_block:{}".format(bookmark_for_sysfee, bookmark_for_block))




        else:
            bookmark_for_sysfee -= 1
            time.sleep(3)




