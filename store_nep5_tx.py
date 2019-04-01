import time
from sqlalchemy.orm import sessionmaker

from config import setting
from data_model.block_info_model import engine, BookmarkForBlock, Tx
from data_model.nep5_model import InvokeTx,BookmarkForNep5, neo_table_engine
from neo_cli import NeoCliRpc
from project_log import setup_logger
from utils.utils import TRANSACTION_TYPE, hex2address, hex2interger


def store_nep5_tx(session,executions, txid, block_height, block_time):
    for execution in executions:
        for notification in execution.get("notifications"):
            contract = notification["contract"]
            try:
                if bytearray.fromhex(notification["state"]["value"][0]["value"]).decode() != "transfer":
                    continue
            except:
                continue
            address_from = hex2address(notification["state"]["value"][1]["value"])
            address_to = hex2address(notification["state"]["value"][2]["value"])
            value = hex2interger(notification["state"]["value"][3]["value"]) if notification["state"]["value"][3][
                                                                                    "type"] != "Integer" \
                else notification["state"]["value"][3]["value"]

            if address_from and address_to and value:
                InvokeTx.save(session=session,
                              tx_id=txid, contract=contract, address_from=address_from, address_to=address_to,
                              value=str(value), vm_state=execution["vmstate"], block_timestamp=block_time,
                              block_height=block_height)




if __name__ == "__main__":

    logger = setup_logger()
    neo_cli_rpc = NeoCliRpc(setting.NEOCLIURL)

    NeoTableSession = sessionmaker(bind=neo_table_engine)
    BlockInfoSession = sessionmaker(bind=engine)

    nep5_session = NeoTableSession()
    #加载本地同步的快高
    bookmarkForNep5 = BookmarkForNep5.query(nep5_session)

    if bookmarkForNep5:
        bookmark_for_nep5 = bookmarkForNep5.height
    else:
        bookmark_for_nep5 = -1
        bookmarkForNep5=BookmarkForNep5.save(nep5_session,bookmark_for_nep5)



    block_interval = 1000

    while True:
        bookmark_for_nep5 += 1
        block_info_session = BlockInfoSession()
        bookmarkForBlock=BookmarkForBlock.query(block_info_session)
        bookmark_for_block = bookmarkForBlock.height

        if bookmark_for_nep5 + block_interval > bookmark_for_block:
            block_interval = 0

        if bookmark_for_nep5 <= bookmark_for_block.height:
            exist_instance = block_info_session.query(Tx).filter(Tx.block_height >= bookmark_for_nep5,
                                                                 Tx.block_height <= bookmark_for_nep5 + block_interval,
                                                                 Tx.tx_type == TRANSACTION_TYPE.INVOKECONTRACT).all()
            if exist_instance:
                for tx in exist_instance:
                    tx_id=tx.tx_id
                    tx_type=tx.tx_type
                    block_height=tx.block_height
                    block_time=tx.block_time

                    try:
                        content = neo_cli_rpc.get_application_log(tx_id)
                    except Exception as e:
                        logger.error(e)
                        content = None

                    if not content:
                        continue

                    if not content.get("executions"):
                        continue

                    store_nep5_tx(nep5_session,content.get("executions"),content.get("txid"),block_height,block_time)

            # break
            bookmark_for_nep5 += block_interval
            bookmarkForNep5.height = bookmark_for_nep5
            BookmarkForNep5.update(nep5_session,bookmarkForNep5)

            try:
                nep5_session.commit()
            except Exception as e:
                logger.error(e)
                nep5_session.rollback()
                raise e
            finally:
                nep5_session.close()

            logger.info("bookmark_nep5:{} bookmark_block:{}".format(bookmark_for_nep5, bookmark_for_block))

        else:
            time.sleep(3)




