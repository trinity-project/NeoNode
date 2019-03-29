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




class BookmarkForClaim(NeoTableBase):
    __tablename__ = 'bookmark_for_claim'
    id = Column(Integer, primary_key=True)
    height = Column(Integer)

    @staticmethod
    def query(session):
        exist_instance=session.query(BookmarkForClaim).first()
        return exist_instance
    @staticmethod
    def save(session,height):
        new_instance = BookmarkForClaim(height=height)
        session.add(new_instance)
        session.commit()
        return new_instance
    @staticmethod
    def update(session,exist_instance):
        session.add(exist_instance)





class ClaimTx(NeoTableBase):
    __tablename__ = 'claim_tx'
    id = Column(Integer, primary_key=True)
    tx_id = Column(String(66))
    address_to = Column(String(40),index=True)
    value = Column(String(30))
    claims = Column(LONGTEXT)
    block_timestamp=Column(Integer)



    @staticmethod
    def save(session,tx_id,address_to,value,block_timestamp,claims):
        new_instance = ClaimTx(tx_id=tx_id,address_to=address_to,value=value,
                                block_timestamp=block_timestamp,claims=claims)
        session.add(new_instance)




NeoTableBase.metadata.create_all(neo_table_engine)
