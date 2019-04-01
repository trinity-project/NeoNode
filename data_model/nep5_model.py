import pymysql

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.orm import sessionmaker

from config import setting





pymysql.install_as_MySQLdb()




neo_table_engine = create_engine('mysql://%s:%s@%s/%s' %(setting.MYSQLDATABASE["user"],
                                               setting.MYSQLDATABASE["passwd"],
                                               setting.MYSQLDATABASE["host"],
                                               setting.MYSQLDATABASE["db_neo_table"]
                                                            ),
                                   pool_recycle=3600,pool_size=100,pool_pre_ping=True)





NeoTableSession = sessionmaker(bind=neo_table_engine)

NeoTableBase = declarative_base()




class BookmarkForNep5(NeoTableBase):
    __tablename__ = 'bookmark_for_nep5'
    id = Column(Integer, primary_key=True)
    height = Column(Integer)

    @staticmethod
    def query(session):
        exist_instance=session.query(BookmarkForNep5).first()
        session.close()
        return exist_instance
    @staticmethod
    def save(session,height):
        new_instance = BookmarkForNep5(height=height)
        session.add(new_instance)
        return new_instance
    @staticmethod
    def update(session,exist_instance):
        session.add(exist_instance)





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



    @staticmethod
    def save(session,tx_id,contract,address_from,address_to,value,vm_state,block_timestamp,block_height):
        new_instance = InvokeTx(tx_id=tx_id,
                                contract=contract,address_from=address_from,
                                address_to=address_to,value=value,vm_state=vm_state,
                                block_timestamp=block_timestamp,block_height=block_height,
                                )
        session.add(new_instance)


NeoTableBase.metadata.create_all(neo_table_engine)
