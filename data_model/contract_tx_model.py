import pymysql

from sqlalchemy.dialects.mysql import LONGTEXT
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Text, create_engine, UniqueConstraint
from sqlalchemy.orm import sessionmaker

from config import setting
from project_log import setup_mylogger

logger=setup_mylogger()




pymysql.install_as_MySQLdb()


block_info_engine = create_engine('mysql://%s:%s@%s/%s' %(setting.MYSQLDATABASE["user"],
                                               setting.MYSQLDATABASE["passwd"],
                                               setting.MYSQLDATABASE["host"],
                                               setting.MYSQLDATABASE["db_block_info"]),
                                  pool_recycle=3600,pool_size=100,pool_pre_ping=True)

neo_table_engine = create_engine('mysql://%s:%s@%s/%s' %(setting.MYSQLDATABASE["user"],
                                               setting.MYSQLDATABASE["passwd"],
                                               setting.MYSQLDATABASE["host"],
                                               setting.MYSQLDATABASE["db_neo_table"]
                                                            ),
                                   pool_recycle=3600,pool_size=100,pool_pre_ping=True)





BlockInfoSession = sessionmaker(bind=block_info_engine)
NeoTableSession = sessionmaker(bind=neo_table_engine)

BlockInfoBase = declarative_base()
NeoTableBase = declarative_base()




class BookmarkForContractTx(NeoTableBase):
    __tablename__ = 'bookmark_for_contract_tx'
    id = Column(Integer, primary_key=True)
    height = Column(Integer)

    @staticmethod
    def query():
        session=NeoTableSession()
        exist_instance=session.query(BookmarkForContractTx).first()
        session.close()
        return exist_instance
    @staticmethod
    def save(height):
        session=NeoTableSession()
        new_instance = BookmarkForContractTx(height=height)
        session.add(new_instance)
        try:
            session.commit()
        except:
            session.rollback()
        finally:
            session.close()
        return new_instance
    @staticmethod
    def update(exist_instance):
        session=NeoTableSession()
        session.add(exist_instance)
        try:
            session.commit()
        except:
            session.rollback()
        finally:
            session.close()

class BookmarkForBlock(BlockInfoBase):
    __tablename__ = 'bookmark_for_block'
    id = Column(Integer, primary_key=True)
    height = Column(Integer)

    @staticmethod
    def query():
        session=BlockInfoSession()
        exist_instance=session.query(BookmarkForBlock).first()
        session.close()
        return exist_instance

class Tx(BlockInfoBase):
    __tablename__ = 'tx'
    id = Column(Integer, primary_key=True)
    tx_id = Column(String(66),unique=True)
    tx_type = Column(String(32))
    block_height=Column(Integer,index=True)
    block_time=Column(Integer)
    vin = Column(LONGTEXT)
    vout = Column(LONGTEXT)
    script=Column(Text)


    @staticmethod
    def query(block_height):
        session=BlockInfoSession()
        exist_instance=session.query(Tx).filter(Tx.block_height==block_height).all()
        session.close()
        return exist_instance



class Vin(NeoTableBase):
    __tablename__ = 'vin'
    id = Column(Integer, primary_key=True)
    tx_id = Column(String(66))
    vout_number = Column(String(6))
    address = Column(String(40))
    asset_id = Column(String(66))
    value = Column(String(30))




    @staticmethod
    def query(session,tx_id,vout_number):
        exist_instance=session.query(Vin).filter(Vin.tx_id==tx_id,
                                                  Vin.vout_number==vout_number).first()
        return exist_instance


class ContractTxMapping(NeoTableBase):
    __tablename__ = 'contract_tx_mapping'
    id = Column(Integer, primary_key=True)
    tx_id = Column(String(66))
    address = Column(String(40),index=True)




    @staticmethod
    def save(session,tx_id,address):
        new_instance = ContractTxMapping(tx_id=tx_id,address=address)
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




class HandledTx(NeoTableBase):
    __tablename__ = 'handled_tx_for_contract_tx'
    id = Column(Integer, primary_key=True)
    tx_id = Column(String(66),unique=True)


    @staticmethod
    def query(session,tx_id):
        exist_instance = session.query(HandledTx).filter(HandledTx.tx_id==tx_id).first()
        return exist_instance

    @staticmethod
    def save(session,tx_id):
        new_instance = HandledTx(tx_id=tx_id)
        session.begin(subtransactions=True)
        try:
            session.add(new_instance)
            session.commit()
        except Exception as e:
            logger.error(e)
            session.rollback()

NeoTableBase.metadata.create_all(neo_table_engine)
