import time
from sqlalchemy.orm import sessionmaker

from config import setting
from data_model.block_info_model import engine, BookmarkForBlock, Tx
from neo_cli import NeoCliRpc
from project_log.my_log import setup_logger

from data_model.token_model import BookmarkForToken, Token, neo_table_engine
from utils.utils import TRANSACTION_TYPE

if __name__ == "__main__":
    logger = setup_logger()
    neo_cli_rpc = NeoCliRpc(setting.NEOCLIURL)

    NeoTableSession = sessionmaker(bind=neo_table_engine)
    BlockInfoSession = sessionmaker(bind=engine)

    token_session = NeoTableSession()


    bookmarkForToken = BookmarkForToken.query(token_session)
    if bookmarkForToken:
        bookmark_for_token = bookmarkForToken.height
    else:
        bookmark_for_token = -1
        bookmarkForToken = BookmarkForToken.save(token_session,bookmark_for_token)

    while True:
        bookmark_for_token += 1
        block_info_session = BlockInfoSession()
        bookmark_for_block = BookmarkForBlock.query(block_info_session)

        if bookmark_for_token <= bookmark_for_block.height:
            exist_instance = block_info_session.query(Tx).filter(Tx.block_height==bookmark_for_token,
                                                                 Tx.tx_type==TRANSACTION_TYPE.INVOKECONTRACT)
            if exist_instance:
                for tx in exist_instance:
                    tx_id = tx.tx_id
                    tx_type = tx.tx_type
                    try:
                        content = neo_cli_rpc.get_application_log(tx_id)
                    except Exception as e:
                        logger.error(e)
                        content = None

                    if not content:
                        continue

                    if not content.get("executions"):
                        continue

                    for execution in content.get("executions"):
                        for notification in execution.get("notifications"):
                            contract = notification["contract"]
                            try:
                                if bytearray.fromhex(notification["state"]["value"][0]["value"]).decode() != "transfer":
                                    continue

                                if Token.query_token(token_session,contract):
                                    continue
                                try:
                                    token_info = neo_cli_rpc.get_token_info(contract)
                                except Exception as e:
                                    logger.error(e)
                                    token_info = None

                                if token_info:
                                    logger.info("store token {}".format(contract))
                                    Token.save(token_session,contract, token_info[0], token_info[1], token_info[2],
                                               "NEP-5", "NEO",
                                               "https://appserver.trinity.ink/static/icon/{}.png".format(token_info[1]))

                            except Exception as e:
                                logger.info(notification)
                                logger.error("contract address:{},error{}".format(contract, e))





            bookmarkForToken.height = bookmark_for_token
            BookmarkForToken.update(token_session,bookmarkForToken)
            try:
                token_session.commit()
            except Exception as e:
                logger.error(e)
                token_session.rollback()
            finally:
                token_session.close()

            logger.info("bookmark token :{},bookmark block :{}".format(bookmark_for_token,bookmark_for_block))




        else:
            bookmark_for_token -= 1
            time.sleep(3)

        block_info_session.close()




