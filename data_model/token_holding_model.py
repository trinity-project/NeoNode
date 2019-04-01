import pymysql

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, create_engine,UniqueConstraint
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




class BookmarkForTokenHolding(NeoTableBase):
    __tablename__ = 'bookmark_for_token_holding'
    id = Column(Integer, primary_key=True)
    height = Column(Integer)

    @staticmethod
    def query(session):
        exist_instance=session.query(BookmarkForTokenHolding).first()
        return exist_instance
    @staticmethod
    def save(session,height):
        new_instance = BookmarkForTokenHolding(height=height)
        session.add(new_instance)

        return new_instance
    @staticmethod
    def update(session,exist_instance):
        session.add(exist_instance)





class TokenHolding(NeoTableBase):
    __tablename__ = 'token_holding'
    id = Column(Integer, primary_key=True)
    contract = Column(String(42))
    address = Column(String(40),index=True)

    __table_args__ = (
        UniqueConstraint('address', 'contract'),
    )


    @staticmethod
    def query(session,contract,address):
        exist_instance = session.query(TokenHolding).filter(TokenHolding.address == contract,TokenHolding.address == address).first()
        return exist_instance
    @staticmethod
    def save(session,contract,address):
        new_instance = TokenHolding(contract=contract, address=address)
        session.add(new_instance)



NeoTableBase.metadata.create_all(neo_table_engine)
