import pymysql

from sqlalchemy.dialects.mysql import LONGTEXT
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Text, create_engine,UniqueConstraint
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




class BookmarkForNep5(NeoTableBase):
    __tablename__ = 'bookmark_for_nep5'
    id = Column(Integer, primary_key=True)
    height = Column(Integer)

    @staticmethod
    def query():
        session=NeoTableSession()
        exist_instance=session.query(BookmarkForNep5).first()
        session.close()
        return exist_instance
    @staticmethod
    def save(height):
        session=NeoTableSession()
        new_instance = BookmarkForNep5(height=height)
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
    sys_fee = Column(String(16))
    net_fee = Column(String(16))


    @staticmethod
    def query(block_height,block_interval,tx_type):
        session=BlockInfoSession()
        exist_instance=session.query(Tx).filter(Tx.block_height>=block_height,Tx.block_height<=block_height+block_interval,
                                                Tx.tx_type==tx_type).all()
        session.close()
        return exist_instance


class InvokeTx(NeoTableBase):
    __tablename__ = 'invoke_tx'
    id = Column(Integer, primary_key=True)
    tx_id = Column(String(66))
    contract = Column(String(42))
    address_from = Column(String(40),index=True)
    address_to = Column(String(40),index=True)
    value = Column(String(30))
    vm_state = Column(String(16))
    block_timestamp=Column(Integer)
    block_height=Column(Integer)
    md5_of_tx = Column(String(32),unique=True)



    @staticmethod
    def save(session,tx_id,contract,address_from,address_to,value,vm_state,block_timestamp,block_height,md5_of_tx):
        new_instance = InvokeTx(tx_id=tx_id,
                                contract=contract,address_from=address_from,
                                address_to=address_to,value=value,vm_state=vm_state,
                                block_timestamp=block_timestamp,block_height=block_height,
                                md5_of_tx = md5_of_tx)
        session.add(new_instance)


NeoTableBase.metadata.create_all(neo_table_engine)
