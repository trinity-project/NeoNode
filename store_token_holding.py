import time

from sqlalchemy.orm import sessionmaker

from config import setting
from data_model.block_info_model import engine, BookmarkForBlock, Tx
from data_model.token_holding_model import BookmarkForTokenHolding, TokenHolding, neo_table_engine
from neo_cli import NeoCliRpc
from project_log import setup_logger
from utils.utils import hex2address, TRANSACTION_TYPE


def store_token_holding(session,executions):
    for execution in executions:
        if execution.get("vmstate") != "HALT, BREAK":
            continue
        for notification in execution.get("notifications"):
            contract = notification["contract"]
            try:
                if bytearray.fromhex(notification["state"]["value"][0]["value"]).decode() != "transfer":
                    continue
            except:
                continue
            address_to = hex2address(notification["state"]["value"][2]["value"])
            TokenHolding.save(session,contract, address_to)



if __name__ == "__main__":

    logger = setup_logger()
    neo_cli_rpc = NeoCliRpc(setting.NEOCLIURL)

    NeoTableSession = sessionmaker(bind=neo_table_engine)
    BlockInfoSession = sessionmaker(bind=engine)

    token_session = NeoTableSession()

    #加载本地同步的快高
    bookmarkForTokenHolding = BookmarkForTokenHolding.query(token_session)

    if bookmarkForTokenHolding:
        bookmark_for_token_holding = bookmarkForTokenHolding.height
    else:
        bookmark_for_token_holding = -1
        bookmarkForTokenHolding=BookmarkForTokenHolding.save(token_session,bookmark_for_token_holding)








    block_interval = 1000

    while True:
        bookmark_for_token_holding += 1
        block_info_session = BlockInfoSession()
        bookmarkForBlock=BookmarkForBlock.query(block_info_session)
        bookmark_for_block = bookmarkForBlock.height

        if bookmark_for_token_holding + block_interval > bookmark_for_block:
            block_interval = 0

        if bookmark_for_token_holding <= bookmark_for_block:
            exist_instance = block_info_session.query(Tx).filter(Tx.block_height >= bookmark_for_token_holding,
                                                                 Tx.block_height <= bookmark_for_token_holding + block_interval,
                                                                 Tx.tx_type == TRANSACTION_TYPE.INVOKECONTRACT).all()
            if exist_instance:
                for tx in exist_instance:
                    tx_id=tx.tx_id
                    try:
                        content = neo_cli_rpc.get_application_log(tx_id)
                    except Exception as e:
                        logger.error(e)
                        content = None

                    if not content:
                        continue

                    if not content.get("executions"):
                        continue

                    store_token_holding(bookmark_for_token_holding,content.get("executions"))

            # break
            bookmark_for_token_holding += block_interval
            bookmarkForTokenHolding.height = bookmark_for_token_holding
            BookmarkForTokenHolding.update(bookmark_for_token_holding,bookmarkForTokenHolding)

            logger.info("bookmark_token_holding:{} bookmark_block:{}".format(bookmark_for_token_holding,
                                                                             bookmark_for_block))




        else:
            bookmark_for_token_holding -= 1
            time.sleep(3)




