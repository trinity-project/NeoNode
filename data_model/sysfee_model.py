import pymysql

from sqlalchemy.dialects.mysql import LONGTEXT
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Text, create_engine
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




class BookmarkForSysfee(NeoTableBase):
    __tablename__ = 'bookmark_for_sysfee'
    id = Column(Integer, primary_key=True)
    height = Column(Integer)

    @staticmethod
    def query():
        session=NeoTableSession()
        exist_instance=session.query(BookmarkForSysfee).first()
        session.close()
        return exist_instance
    @staticmethod
    def save(height):
        session=NeoTableSession()
        new_instance = BookmarkForSysfee(height=height)
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
    def query(block_height):
        session=BlockInfoSession()
        exist_instance=session.query(Tx).filter(Tx.block_height==block_height).all()
        session.close()
        return exist_instance


class Sysfee(NeoTableBase):
    __tablename__ = 'sysfee'
    id = Column(Integer, primary_key=True)
    block_height=Column(Integer)
    sys_fee = Column(String(16))


    @staticmethod
    def query(block_height):
        session=NeoTableSession()
        exist_instance=session.query(Sysfee).filter(Sysfee.block_height==block_height).first()
        session.close()
        return exist_instance

    @staticmethod
    def save(session,block_height,sys_fee):
        new_instance = Sysfee(block_height=block_height,sys_fee=sys_fee)
        session.add(new_instance)


NeoTableBase.metadata.create_all(neo_table_engine)
