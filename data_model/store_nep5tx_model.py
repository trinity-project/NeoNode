#!/usr/bin/env python
# coding=utf-8
import pymysql

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Boolean, create_engine, DECIMAL, Index, or_
from sqlalchemy.orm import sessionmaker
from config import setting

from project_log import setup_mylogger

logger=setup_mylogger()


pymysql.install_as_MySQLdb()
engine = create_engine('mysql://%s:%s@%s/%s' %(setting.MYSQLDATABASE["user"],
                                               setting.MYSQLDATABASE["passwd"],
                                               setting.MYSQLDATABASE["host"],
                                               setting.MYSQLDATABASE["db_account_info"]),
                        pool_recycle=3600,pool_size=100
                       )

Session = sessionmaker(bind=engine)
Base = declarative_base()


class InvokeTx(Base):
    __tablename__ = 'invoke_tx'
    id = Column(Integer, primary_key=True)
    tx_id = Column(String(66))
    contract = Column(String(42))
    address_from = Column(String(40))
    address_to = Column(String(40))
    value = Column(DECIMAL(17,8))
    vm_state = Column(String(16))
    has_pushed=Column(Boolean,default=False)
    block_timestamp=Column(Integer)
    block_height=Column(Integer)


    __table_args__ = (
        Index('address_from', 'address_to','vm_state','hash_pushed'),
    )


    @staticmethod
    def query():
        session = Session()
        exist_instance = session.query(InvokeTx).filter(
            or_(InvokeTx.address_from == setting.FUNDING_ADDRESS,
                InvokeTx.address_to == setting.FUNDING_ADDRESS),
            InvokeTx.vm_state == "HALT, BREAK",
            InvokeTx.has_pushed==0
        ).first()
        session.close()

        return exist_instance

    @staticmethod
    def save(tx_id,contract,address_from,address_to,value,vm_state,block_timestamp,block_height):
        session=Session()
        new_instance = InvokeTx(tx_id=tx_id,
                                contract=contract,address_from=address_from,
                                address_to=address_to,value=value,vm_state=vm_state,
                                block_timestamp=block_timestamp,block_height=block_height)
        session.add(new_instance)
        try:
            session.commit()
            logger.info("txid:{},addressFrom:{},addressTo:{},value:{}".format(tx_id, address_from, address_to, value))
        except:
            logger.error("store error txid:{},addressFrom:{},addressTo:{},value:{}".format(tx_id, address_from, address_to, value))
            session.rollback()
        finally:
            session.close()

    @staticmethod
    def update(exist_instance):
        session = Session()
        session.add(exist_instance)
        try:
            session.commit()
        except:
            session.rollback()
        finally:
            session.close()


Base.metadata.create_all(engine)









