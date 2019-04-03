import json
import time
from sqlalchemy.orm import sessionmaker

from data_model.block_info_model import engine,Tx
from data_model.utxo_model import BookmarkForUtxo,Utxo
from data_model.contract_tx_model import BookmarkForContractTx,ContractTxDetail,ContractTxMapping, neo_table_engine
from project_log import setup_logger
from utils.utils import TRANSACTION_TYPE



#存储全局资产交易
def store_contract_tx(session,tx_id,vin,vout,block_height,block_time):

    address_set = set()  #inputs 和 outputs 所有地址集合
    new_vin = []
    for _vin in vin:
        vin_txid = _vin["txid"]
        vin_vout_number = _vin["vout"]
        utxo_instance = Utxo.query(session,vin_txid, vin_vout_number)

        if utxo_instance:
            address_set.add((utxo_instance.address,utxo_instance.asset_id,block_height))
            new_vin.append(dict(address=utxo_instance.address,asset=utxo_instance.asset_id,value=utxo_instance.value))

        else:
            raise Exception("handle tx:{} lost utxo ({},{})".format(tx_id,vin_txid, vin_vout_number))

    ContractTxDetail.save(session,tx_id,json.dumps(new_vin),json.dumps(vout),block_time,block_height)

    for _vout in vout:
        address_set.add((_vout["address"],_vout["asset"],block_height))

    for address,asset,block_height in address_set:
        ContractTxMapping.save(session,tx_id,address,asset,block_height)

if __name__ == "__main__":
    logger = setup_logger()

    BlockInfoSession = sessionmaker(bind=engine)
    NeoTableSession = sessionmaker(bind=neo_table_engine)

    contract_tx_session = NeoTableSession()


    # 加载本地同步的快高
    bookmarkForContractTx = BookmarkForContractTx.query(contract_tx_session)

    if bookmarkForContractTx:
        bookmark_for_contract_tx = bookmarkForContractTx.height
    else:
        bookmark_for_contract_tx = -1
        bookmarkForContractTx = BookmarkForContractTx.save(contract_tx_session,bookmark_for_contract_tx)

    while True:

        bookmark_for_contract_tx += 1
        block_info_session = BlockInfoSession()
        query_height_session = NeoTableSession()
        bookmarkForUtxo = BookmarkForUtxo.query(query_height_session)
        bookmark_for_utxo = bookmarkForUtxo.height
        query_height_session.close()

        if bookmark_for_contract_tx <= bookmark_for_utxo:
            exist_instance=block_info_session.query(Tx).filter(Tx.block_height==bookmark_for_contract_tx,Tx.tx_type==TRANSACTION_TYPE.CONTRACT).all()

            if  exist_instance:
                for tx in exist_instance:
                    tx_id=tx.tx_id
                    tx_type=tx.tx_type
                    block_height=tx.block_height
                    block_time=tx.block_time
                    vin=json.loads(tx.vin)
                    vout=json.loads(tx.vout)

                    store_contract_tx(contract_tx_session, tx_id, vin, vout, block_height, block_time)



            bookmarkForContractTx.height = bookmark_for_contract_tx
            BookmarkForContractTx.update(contract_tx_session,bookmarkForContractTx)

            try:
                contract_tx_session.commit()
            except Exception as e:
                contract_tx_session.rollback()
                raise e


            logger.info("bookmark_contract_tx:{} bookmark_utxo:{}".format(bookmark_for_contract_tx, bookmark_for_utxo))



        else:
            bookmark_for_contract_tx -= 1
            time.sleep(3)

        block_info_session.close()


