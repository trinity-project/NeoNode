import json
import time


from data_model.contract_tx_model import Tx, logger, BookmarkForBlock, NeoTableSession, ContractTx, \
    BookmarkForContractTx, Vin, ContractTxDetail, HandledTx

#加载本地同步的快高
bookmarkForContractTx = BookmarkForContractTx.query()

if bookmarkForContractTx:
    bookmark_for_contract_tx=bookmarkForContractTx.height
else:
    bookmark_for_contract_tx=0
    bookmarkForContractTx=BookmarkForContractTx.save(bookmark_for_contract_tx)



#存储全局资产交易
def store_contract_tx(session,tx_id,vin,vout,block_height,block_time):

    address_set = set()  #inputs 和 outputs 所有地址集合
    new_vin = []
    for _vin in vin:
        vin_txid = _vin["txid"]
        vin_vout_number = _vin["vout"]
        vin_instance = Vin.query(session,vin_txid, vin_vout_number)

        if vin_instance:
            address_set.add(vin_instance.address)
            new_vin.append(dict(address=vin_instance.address,asset_id=vin_instance.asset_id,amount=vin_instance.value))

        else:
            raise Exception("lost vin ({},{})".format(vin_txid, vin_vout_number))

    ContractTxDetail.save(session,tx_id,json.dumps(new_vin),json.dumps(vout),block_time,block_height)

    for _vout in vout:
        address_set.add(_vout["address"])

    for address in address_set:
        ContractTx.save(session,tx_id,address)



while True:
    bookmark_for_block=BookmarkForBlock.query()
    logger.info("bookmark_contract_tx:{} bookmark_block:{}".format(bookmark_for_contract_tx,bookmark_for_block.height))
    if not bookmark_for_block:
        continue



    if bookmark_for_contract_tx < bookmark_for_block.height:
        exist_instance=Tx.query(bookmark_for_contract_tx)
        if  exist_instance:
            for tx in exist_instance:
                tx_id=tx.tx_id
                tx_type=tx.tx_type
                block_height=tx.block_height
                block_time=tx.block_time
                vin=json.loads(tx.vin)
                vout=json.loads(tx.vout)

                session = NeoTableSession(autocommit=True)
                handled_tx = HandledTx.query(session,tx_id)

                if handled_tx:
                    logger.info("tx {} has been handled".format(tx_id))
                    continue
                try:
                    session.begin(subtransactions=True)
                    store_contract_tx(session, tx_id, vin, vout, block_height, block_time)
                    session.commit()
                except Exception as e:
                    session.rollback()
                    raise e
                finally:
                    session.close()

        bookmark_for_contract_tx += 1
        bookmarkForContractTx.height = bookmark_for_contract_tx
        BookmarkForContractTx.update(bookmarkForContractTx)




    else:
        time.sleep(10)




