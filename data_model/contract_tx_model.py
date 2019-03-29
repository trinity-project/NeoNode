import pymysql

from sqlalchemy.dialects.mysql import LONGTEXT
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, create_engine

from config import setting



pymysql.install_as_MySQLdb()




neo_table_engine = create_engine('mysql://%s:%s@%s/%s' %(setting.MYSQLDATABASE["user"],
                                               setting.MYSQLDATABASE["passwd"],
                                               setting.MYSQLDATABASE["host"],
                                               setting.MYSQLDATABASE["db_neo_table"]
                                                            ),
                                   pool_recycle=3600,pool_size=100,pool_pre_ping=True)







NeoTableBase = declarative_base()




class BookmarkForContractTx(NeoTableBase):
    __tablename__ = 'bookmark_for_contract_tx'
    id = Column(Integer, primary_key=True)
    height = Column(Integer)

    @staticmethod
    def query(session):
        exist_instance=session.query(BookmarkForContractTx).first()
        return exist_instance
    @staticmethod
    def save(session,height):
        new_instance = BookmarkForContractTx(height=height)
        session.add(new_instance)
        return new_instance
    @staticmethod
    def update(session,exist_instance):
        session.add(exist_instance)





class ContractTxMapping(NeoTableBase):
    __tablename__ = 'contract_tx_mapping'
    id = Column(Integer, primary_key=True)
    tx_id = Column(String(66))
    asset = Column(String(66))
    address = Column(String(40),index=True)
    block_height = Column(Integer)




    @staticmethod
    def save(session,tx_id,address,asset,block_height):
        new_instance = ContractTxMapping(tx_id=tx_id,address=address,asset=asset,block_height=block_height)
        session.add(new_instance)



class ContractTxDetail(NeoTableBase):
    __tablename__ = 'contract_tx_detail'
    id = Column(Integer, primary_key=True)
    tx_id = Column(String(66),unique=True)
    inputs = Column(LONGTEXT)
    outputs = Column(LONGTEXT)
    block_timestamp=Column(Integer)
    block_height=Column(Integer)



    @staticmethod
    def save(session,tx_id,inputs,outputs,block_timestamp,block_height):
        new_instance = ContractTxDetail(tx_id=tx_id,
                                inputs=inputs,
                                outputs=outputs,
                                block_timestamp=block_timestamp,block_height=block_height
                                )
        session.add(new_instance)




NeoTableBase.metadata.create_all(neo_table_engine)
