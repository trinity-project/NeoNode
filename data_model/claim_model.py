import pymysql

from sqlalchemy.dialects.mysql import LONGTEXT
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Text, create_engine, Boolean
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




class BookmarkForClaim(NeoTableBase):
    __tablename__ = 'bookmark_for_claim'
    id = Column(Integer, primary_key=True)
    height = Column(Integer)

    @staticmethod
    def query():
        session=NeoTableSession()
        exist_instance=session.query(BookmarkForClaim).first()
        session.close()
        return exist_instance
    @staticmethod
    def save(height):
        session=NeoTableSession()
        new_instance = BookmarkForClaim(height=height)
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
    claims = Column(Text)
    sys_fee = Column(String(16))
    net_fee = Column(String(16))

    @staticmethod
    def query(block_height,block_interval,tx_type):
        session=BlockInfoSession()
        exist_instance=session.query(Tx).filter(Tx.block_height>=block_height,Tx.block_height<=block_height+block_interval,
                                                Tx.tx_type==tx_type).all()
        session.close()
        return exist_instance


class ClaimTx(NeoTableBase):
    __tablename__ = 'claim_tx'
    id = Column(Integer, primary_key=True)
    tx_id = Column(String(66))
    address_to = Column(String(40),index=True)
    value = Column(String(30))
    block_timestamp=Column(Integer)



    @staticmethod
    def save(session,tx_id,address_to,value,block_timestamp):
        new_instance = ClaimTx(tx_id=tx_id,address_to=address_to,value=value,
                                block_timestamp=block_timestamp)
        session.add(new_instance)


class Utxo(NeoTableBase):
    __tablename__ = 'utxo'
    id = Column(Integer, primary_key=True)
    tx_id = Column(String(66))
    vout_number = Column(String(6))
    address = Column(String(40),index=True)
    asset_id = Column(String(66))
    value = Column(String(16))
    start_block = Column(Integer)
    end_block = Column(Integer)
    is_used = Column(Boolean,default=False)
    is_claimed = Column(Boolean,default=False)
    gen_gas = Column(String(16))



    @staticmethod
    def query(session,tx_id,vout_number):
        exist_instance=session.query(Utxo).filter(Utxo.tx_id==tx_id,
                                                  Utxo.vout_number==vout_number).first()
        return exist_instance



    @staticmethod
    def update(session,instanse):
        session.begin(subtransactions=True)
        try:
            session.add(instanse)
            session.commit()
        except Exception as e:
            logger.error(e)
            session.rollback()


NeoTableBase.metadata.create_all(neo_table_engine)
