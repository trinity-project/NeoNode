import pymysql
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, create_engine,String

from config import setting





pymysql.install_as_MySQLdb()




neo_table_engine = create_engine('mysql://%s:%s@%s/%s' %(setting.MYSQLDATABASE["user"],
                                               setting.MYSQLDATABASE["passwd"],
                                               setting.MYSQLDATABASE["host"],
                                               setting.MYSQLDATABASE["db_neo_table"]
                                                            ),
                                   pool_recycle=3600,pool_size=100,pool_pre_ping=True)





NeoTableBase = declarative_base()



class BookmarkForToken(NeoTableBase):
    __tablename__ = 'bookmark_for_token'
    id = Column(Integer, primary_key=True)
    height = Column(Integer)

    @staticmethod
    def query(session):
        exist_instance=session.query(BookmarkForToken).first()
        return exist_instance
    @staticmethod
    def save(session,height):
        new_instance = BookmarkForToken(height=height)
        session.add(new_instance)
        return new_instance

    @staticmethod
    def update(session,exist_instance):
        session.add(exist_instance)




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
    def query_token(session,address):
        exist_instance = session.query(Token).filter(Token.address==address).first()
        return exist_instance


    @staticmethod
    def save(session,address,name,symbol,decimal,tokenType,chainType,icon):
        new_instance = Token(address=address, name=name,symbol=symbol,decimal=decimal,
                             token_type = tokenType,chain_type=chainType,icon=icon)
        session.add(new_instance)







NeoTableBase.metadata.create_all(neo_table_engine)