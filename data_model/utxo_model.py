import pymysql
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, create_engine, UniqueConstraint, Boolean

from config import setting


pymysql.install_as_MySQLdb()


neo_table_engine = create_engine('mysql://%s:%s@%s/%s' %(setting.MYSQLDATABASE["user"],
                                               setting.MYSQLDATABASE["passwd"],
                                               setting.MYSQLDATABASE["host"],
                                               setting.MYSQLDATABASE["db_neo_table"]
                                                            ),
                                   pool_recycle=3600,pool_size=100,pool_pre_ping=True)







BlockInfoBase = declarative_base()
NeoTableBase = declarative_base()




class BookmarkForUtxo(NeoTableBase):
    __tablename__ = 'bookmark_for_utxo'
    id = Column(Integer, primary_key=True)
    height = Column(Integer)

    @staticmethod
    def query(session):
        exist_instance=session.query(BookmarkForUtxo).first()
        return exist_instance
    @staticmethod
    def save(session,height):
        new_instance = BookmarkForUtxo(height=height)
        session.add(new_instance)
        return new_instance
    @staticmethod
    def update(session,exist_instance):
        session.add(exist_instance)



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

    __table_args__ = (
        UniqueConstraint('tx_id', 'vout_number'),
    )


    @staticmethod
    def query(session,tx_id,vout_number):
        exist_instance=session.query(Utxo).filter(Utxo.tx_id==tx_id,
                                                  Utxo.vout_number==vout_number).first()
        return exist_instance

    @staticmethod
    def save(session,tx_id,address,asset_id,vout_number,value,start_block):
        new_instance = Utxo(tx_id=tx_id, address=address, asset_id=asset_id,
                               vout_number=vout_number,value=value,start_block=start_block)

        session.add(new_instance)



    @staticmethod
    def update(session,instanse):
        session.add(instanse)




NeoTableBase.metadata.create_all(neo_table_engine)
