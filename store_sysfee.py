import json
import time

from decimal import Decimal

from data_model.sysfee_model import   Tx, Sysfee, BookmarkForBlock, BookmarkForSysfee, logger, NeoTableSession




class TRANSACTION_TYPE(object):
    CONTRACT="ContractTransaction"
    CLAIM="ClaimTransaction"
    INVOKECONTRACT="InvocationTransaction"

#加载本地同步的快高
bookmarkForSysfee = BookmarkForSysfee.query()

if bookmarkForSysfee:
    bookmark_for_sysfee = bookmarkForSysfee.height
else:
    bookmark_for_sysfee = 0
    bookmarkForSysfee=BookmarkForSysfee.save(bookmark_for_sysfee)



def store_sysfee(session,block_height,sys_fee):

    exist_instance = Sysfee.query(block_height-1)
    if exist_instance:
        pre_sysfee = exist_instance.sys_fee
        Sysfee.save(session,block_height,str(sys_fee + Decimal(pre_sysfee)))
    else:
        Sysfee.save(session, block_height, str(sys_fee))


while True:
    bookmark_for_block=BookmarkForBlock.query()
    logger.info("bookmark_sysfee:{} bookmark_block:{}".format(bookmark_for_sysfee,bookmark_for_block.height))
    if not bookmark_for_block:
        time.sleep(10)
        continue


    if bookmark_for_sysfee < bookmark_for_block.height:
        exist_instance=Tx.query(bookmark_for_sysfee)
        if exist_instance:
            for tx in exist_instance:
                sys_fee = Decimal(tx.sys_fee)
                net_fee = Decimal(tx.net_fee)
                sys_fee += sys_fee


            session = NeoTableSession(autocommit=True)
            try:
                session.begin(subtransactions=True)
                store_sysfee(session,bookmark_for_sysfee,sys_fee)
                session.commit()
            except Exception as e:
                session.rollback()
                raise e
            finally:
                session.close()
        # break
        bookmark_for_sysfee += 1
        bookmarkForSysfee.height = bookmark_for_sysfee
        BookmarkForSysfee.update(bookmarkForSysfee)




    else:
        time.sleep(10)




