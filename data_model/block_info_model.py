import pymysql

from sqlalchemy.dialects.mysql import LONGTEXT
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Text, create_engine, Index
from sqlalchemy.orm import sessionmaker

from config import setting
from project_log import setup_mylogger

logger=setup_mylogger()



pymysql.install_as_MySQLdb()

def _check_database(database_name):
    conn = pymysql.connect(host=setting.MYSQLDATABASE["host"], user=setting.MYSQLDATABASE["user"],
                           passwd=setting.MYSQLDATABASE["passwd"])
    cursor = conn.cursor()
    cursor.execute("""create database if not exists {} """.format(database_name))
    cursor.close()
    conn.commit()
    conn.close()


_check_database("block_info")

engine = create_engine('mysql://%s:%s@%s/%s' %(setting.MYSQLDATABASE["user"],
                                               setting.MYSQLDATABASE["passwd"],
                                               setting.MYSQLDATABASE["host"],
                                               setting.MYSQLDATABASE["db_block_info"]),
                       pool_recycle=3600, pool_size=100,pool_pre_ping=True)


Session = sessionmaker(bind=engine)
Base = declarative_base()



class BookmarkForBlock(Base):
    __tablename__ = 'bookmark_for_block'
    id = Column(Integer, primary_key=True)
    height = Column(Integer)

    @staticmethod
    def query():
        session=Session()
        exist_instance=session.query(BookmarkForBlock).first()
        session.close()
        return exist_instance
    @staticmethod
    def save(height):
        session=Session()
        new_instance = BookmarkForBlock(height=height)
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
        session=Session()
        session.add(exist_instance)
        try:
            session.commit()
        except:
            session.rollback()
        finally:
            session.close()

class Tx(Base):
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
    def save(tx_id,tx_type,block_height,block_time,vin,vout,sys_fee,net_fee,claims):
        session=Session()
        new_instance = Tx(tx_id=tx_id, tx_type=tx_type,block_height=block_height,
                          block_time=block_time,vin =vin,vout=vout,sys_fee=sys_fee,
                          net_fee=net_fee,claims=claims)


        session.add(new_instance)
        try:
            session.commit()

        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()


Base.metadata.create_all(engine)
