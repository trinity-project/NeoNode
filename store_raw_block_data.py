
import json
import time

from config import setting
from neo_cli import NeoCliRpc
from data_model.block_info_model import BookmarkForBlock, Tx, BlockInfoSession
from project_log import setup_logger




if __name__ == "__main__":
    logger = setup_logger()
    neo_cli_rpc = NeoCliRpc(setting.NEOCLIURL)

    #开启mysql会话
    session = BlockInfoSession()
    bookmarkForBlock = BookmarkForBlock.query(session)
    if bookmarkForBlock:
        bookmark_for_block = bookmarkForBlock.height
    else:
        bookmark_for_block = -1
        bookmarkForBlock = BookmarkForBlock.save(session,bookmark_for_block)

    while True:
        bookmark_for_block += 1

        # Neo-cli rpc 有可能不可用
        try:
            block_info = neo_cli_rpc.get_block(bookmark_for_block)
        except Exception as e:
            logger.error(e)
            block_info = None

        #如果 neo-cli rpc 不可用,睡眠几秒,继续请求
        if not block_info:
            time.sleep(3)
            continue

        for tx in block_info["tx"]:
            tx_type=tx["type"]
            tx_id=tx["txid"]
            block_height=block_info["index"]
            block_time=block_info["time"]
            vin=json.dumps(tx["vin"])
            vout=json.dumps(tx["vout"])
            sys_fee = tx["sys_fee"]
            net_fee = tx["net_fee"]
            claims = json.dumps(tx.get("claims",[]))
            Tx.save(session,tx_id,tx_type,block_height,block_time,vin,vout,sys_fee,net_fee,claims=claims)

        bookmarkForBlock.height=bookmark_for_block
        BookmarkForBlock.update(session,bookmarkForBlock)

        #提交mysql 回话
        try:
            session.commit()
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
        logger.info("已入库块高:{}".format(bookmark_for_block))




