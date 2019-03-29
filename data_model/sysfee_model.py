import pymysql
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.orm import sessionmaker

from config import setting




# pymysql.install_as_MySQLdb()


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





# BlockInfoSession = sessionmaker(bind=block_info_engine)
NeoTableSession = sessionmaker(bind=neo_table_engine)

BlockInfoBase = declarative_base()
NeoTableBase = declarative_base()




class BookmarkForSysfee(NeoTableBase):
    __tablename__ = 'bookmark_for_sysfee'
    id = Column(Integer, primary_key=True)
    height = Column(Integer)

    @staticmethod
    def query(session):
        exist_instance=session.query(BookmarkForSysfee).first()
        return exist_instance
    @staticmethod
    def save(session,height):
        new_instance = BookmarkForSysfee(height=height)
        session.add(new_instance)
        return new_instance
    @staticmethod
    def update(session,exist_instance):
        session.add(exist_instance)


class Sysfee(NeoTableBase):
    __tablename__ = 'sysfee'
    id = Column(Integer, primary_key=True)
    block_height=Column(Integer,unique=True)
    sys_fee = Column(String(16))


    @staticmethod
    def query(session,block_height):
        exist_instance=session.query(Sysfee).filter(Sysfee.block_height==block_height).first()
        return exist_instance

    @staticmethod
    def save(session,block_height,sys_fee):
        new_instance = Sysfee(block_height=block_height,sys_fee=sys_fee)
        session.add(new_instance)


NeoTableBase.metadata.create_all(neo_table_engine)
