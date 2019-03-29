import random
import time
import requests


from config import setting
from data_model.token_model import Tx, BookmarkForToken, BookmarkForBlock, Token ,logger






if __name__ == "__main__":

    bookmarkForToken = BookmarkForToken.query()
    if bookmarkForToken:

        bookmark_for_token = bookmarkForToken.height
    else:
        bookmark_for_token = 0
        bookmarkForToken = BookmarkForToken.save(bookmark_for_token)
    while True:
        logger.info(bookmark_for_token)
        bookmark_for_block = BookmarkForBlock.query()
        if not bookmark_for_block:
            continue
        if bookmark_for_token < bookmark_for_block.height:
            exist_instance = Tx.query(bookmark_for_token)
            if exist_instance:
                for tx in exist_instance:
                    tx_id = tx.tx_id
                    tx_type = tx.tx_type

                    if tx_type != TRANSACTION_TYPE.INVOKECONTRACT:
                        continue

                    content = get_application_log(tx_id)

                    if not content.get("executions"):
                        continue

                    for execution in content.get("executions"):
                        for notification in execution.get("notifications"):
                            contract = notification["contract"]
                            try:
                                if bytearray.fromhex(notification["state"]["value"][0]["value"]).decode() != "transfer":
                                    continue

                                if Token.query_token(contract):
                                    continue

                                token_info = get_token_info(contract)
                                if token_info:
                                    logger.info("store token {}".format(contract))
                                    Token.save(contract, token_info[0], token_info[1], token_info[2],
                                               "NEP-5", "NEO",
                                               "https://appserver.trinity.ink/static/icon/{}.png".format(token_info[1]))

                            except Exception as e:
                                logger.info(notification)
                                logger.error("contract address:{},error{}".format(contract, e))





            bookmark_for_token += 1
            bookmarkForToken.height = bookmark_for_token
            BookmarkForToken.update(bookmarkForToken)




        else:
            time.sleep(10)






