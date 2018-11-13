import pymysql
from sqlalchemy.dialects.mysql import LONGTEXT
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, create_engine,String, Text
from sqlalchemy.orm import sessionmaker

from config import setting
from project_log import setup_mylogger

logger=setup_mylogger(logfile="log/store_token.log")




pymysql.install_as_MySQLdb()




block_info_engine = create_engine('mysql://%s:%s@%s/%s' %(setting.MYSQLDATABASE["user"],
                                               setting.MYSQLDATABASE["passwd"],
                                               setting.MYSQLDATABASE["host"],
                                               setting.MYSQLDATABASE["db_block_info"]),
                                  pool_recycle=3600,pool_size=100)

account_info_engine = create_engine('mysql://%s:%s@%s/%s' %(setting.MYSQLDATABASE["user"],
                                               setting.MYSQLDATABASE["passwd"],
                                               setting.MYSQLDATABASE["host"],
                                               setting.MYSQLDATABASE["db_neo_table"]
                                                            ),
                                   pool_recycle=3600,pool_size=100)



BlockInfoSession = sessionmaker(bind=block_info_engine)
NeoTableSession = sessionmaker(bind=account_info_engine)

BlockInfoBase = declarative_base()
NeoTableBase = declarative_base()



class BookmarkForToken(NeoTableBase):
    __tablename__ = 'bookmark_for_token'
    id = Column(Integer, primary_key=True)
    height = Column(Integer)

    @staticmethod
    def query():
        session=NeoTableSession()
        exist_instance=session.query(BookmarkForToken).first()
        session.close()
        return exist_instance
    @staticmethod
    def save(height):
        session=NeoTableSession()
        new_instance = BookmarkForToken(height=height)
        session.add(new_instance)
        try:
            session.commit()
        except:
            session.rollback()
        finally:
            session.close()
        return new_instance



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


class Token(NeoTableBase):
    __tablename__ = 'token'
    id = Column(Integer, primary_key=True)
    address = Column(String(42),unique=True)
    name = Column(String(32),index=True)
    symbol = Column(String(8),index=True)
    decimal = Column(String(2))
    token_type = Column(String(8))
    chain_type = Column(String(8))
    icon = Column(String(256))

    @staticmethod
    def query_token(address):
        session = NeoTableSession()
        exist_instance = session.query(Token).filter(Token.address==address).first()
        return exist_instance


    @staticmethod
    def save(address,name,symbol,decimal,tokenType,chainType,icon):
        session = NeoTableSession()
        new_instance = Token(address=address, name=name,symbol=symbol,decimal=decimal,
                             token_type = tokenType,chain_type=chainType,icon=icon)
        session.add(new_instance)
        try:
            session.commit()
            return True
        except Exception as e:
            return False





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

NeoTableBase.metadata.create_all(account_info_engine)