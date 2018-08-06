import pymysql

from sqlalchemy.dialects.mysql import LONGTEXT
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Text, create_engine, SmallInteger, DECIMAL, Index, Boolean, or_,UniqueConstraint
from sqlalchemy.orm import sessionmaker

from config import setting
from project_log import setup_mylogger

logger=setup_mylogger(logfile="log/store_account_info.log")




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
_check_database("account_info")


block_info_engine = create_engine('mysql://%s:%s@%s/%s' %(setting.MYSQLDATABASE["user"],
                                               setting.MYSQLDATABASE["passwd"],
                                               setting.MYSQLDATABASE["host"],
                                               setting.MYSQLDATABASE["db_block_info"]),
                                  pool_recycle=3600,pool_size=100)

account_info_engine = create_engine('mysql://%s:%s@%s/%s' %(setting.MYSQLDATABASE["user"],
                                               setting.MYSQLDATABASE["passwd"],
                                               setting.MYSQLDATABASE["host"],
                                               setting.MYSQLDATABASE["db_account_info"]
                                                            ),
                                   pool_recycle=3600,pool_size=100)





BlockInfoSession = sessionmaker(bind=block_info_engine)
AccountInfoSession = sessionmaker(bind=account_info_engine)

BlockInfoBase = declarative_base()
AccountInfoBase = declarative_base()


class Balance(AccountInfoBase):
    __tablename__ = 'balance'
    id = Column(Integer, primary_key=True)
    address = Column(String(40),unique=True)
    neo_balance = Column(DECIMAL(17,8),default=0)
    gas_balance =Column(DECIMAL(17,8),default=0)



    @staticmethod
    def query(address):
        session=AccountInfoSession()
        exist_instance=session.query(Balance).filter(Balance.address==address).first()
        session.close()
        return exist_instance


    @staticmethod
    def update(self):
        session=AccountInfoSession()
        session.add(self)
        try:
            session.commit()
        except:
            session.rollback()
        finally:
            session.close()

    @staticmethod
    def save(new_instance):
        session=AccountInfoSession()
        session.add(new_instance)
        try:
            session.commit()
        except:
            session.rollback()
        finally:
            session.close()

class LocalBlockCout(AccountInfoBase):
    __tablename__ = 'local_block_count'
    id = Column(Integer, primary_key=True)
    height = Column(Integer)

    @staticmethod
    def query():
        session=AccountInfoSession()
        exist_instance=session.query(LocalBlockCout).first()
        session.close()
        return exist_instance
    @staticmethod
    def save(height):
        session=AccountInfoSession()
        new_instance = LocalBlockCout(height=height)
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
        session=AccountInfoSession()
        session.add(exist_instance)
        try:
            session.commit()
        except:
            session.rollback()
        finally:
            session.close()

class BlockHeight(BlockInfoBase):
    __tablename__ = 'local_block_count'
    id = Column(Integer, primary_key=True)
    height = Column(Integer)

    @staticmethod
    def query():
        session=BlockInfoSession()
        exist_instance=session.query(BlockHeight).first()
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
    script=Column(Text)


    @staticmethod
    def query(block_height):
        session=BlockInfoSession()
        exist_instance=session.query(Tx).filter(Tx.block_height==block_height).all()
        session.close()
        return exist_instance

class Vout(AccountInfoBase):
    __tablename__ = 'vout'
    id = Column(Integer, primary_key=True)
    tx_id = Column(String(66))
    address = Column(String(40),index=True)
    asset_id = Column(String(66))
    vout_number = Column(SmallInteger)
    value = Column(DECIMAL(17,8))

    __table_args__ = (
        UniqueConstraint('tx_id', 'vout_number'),
    )


    @staticmethod
    def query(tx_id,vout_number):
        session=AccountInfoSession()
        exist_instance=session.query(Vout).filter(Vout.tx_id==tx_id,
                                                  Vout.vout_number==vout_number).first()
        session.close()
        return exist_instance

    @staticmethod
    def save(tx_id,address,asset_id,vout_number,value):
        session=AccountInfoSession()
        new_instance = Vout(tx_id=tx_id, address=address, asset_id=asset_id,
                               vout_number=vout_number,value=value)
        session.add(new_instance)
        try:
            session.commit()
            saved = True
        except Exception as e:
            logger.error(e)
            session.rollback()
            saved = False
        finally:
            session.close()
        return saved
    @staticmethod
    def delete(instanse):
        session=AccountInfoSession()
        session.delete(instanse)
        try:
            session.commit()

        except:
            logger.error("delete vout fail > tx_id:{0} ".format(instanse.tx_id))
            session.rollback()
        finally:
            session.close()

class InvokeTx(AccountInfoBase):
    __tablename__ = 'invoke_tx'
    id = Column(Integer, primary_key=True)
    tx_id = Column(String(66),unique=True)
    contract = Column(String(42))
    address_from = Column(String(40),index=True)
    address_to = Column(String(40),index=True)
    value = Column(DECIMAL(17,8))
    vm_state = Column(String(16))
    has_pushed=Column(Boolean,default=False)
    block_timestamp=Column(Integer,index=True)
    block_height=Column(Integer)


    __table_args__ = (
        Index("multi_index",'address_from', 'address_to','vm_state','has_pushed'),
    )


    @staticmethod
    def query():
        session = AccountInfoSession()
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
        session=AccountInfoSession()
        new_instance = InvokeTx(tx_id=tx_id,
                                contract=contract,address_from=address_from,
                                address_to=address_to,value=value,vm_state=vm_state,
                                block_timestamp=block_timestamp,block_height=block_height)
        session.add(new_instance)
        try:
            session.commit()
        except Exception as e:
            logger.error("store nep5 tx error >txid:{},addressFrom:{},addressTo:{},value:{}\n{}".format(tx_id, address_from, address_to, value,e))
            session.rollback()
        finally:
            session.close()

    @staticmethod
    def update(exist_instance):
        session = AccountInfoSession()
        session.add(exist_instance)
        try:
            session.commit()
        except:
            session.rollback()
        finally:
            session.close()


class ContractTx(AccountInfoBase):
    __tablename__ = 'contract_tx'
    id = Column(Integer, primary_key=True)
    tx_id = Column(String(66),unique=True)
    asset = Column(String(66))
    address_from = Column(String(40),index=True)
    address_to = Column(String(40),index=True)
    value = Column(DECIMAL(17,8))
    block_timestamp=Column(Integer,index=True)
    block_height=Column(Integer)



    @staticmethod
    def save(tx_id,asset,address_from,address_to,value,block_timestamp,block_height):
        session=AccountInfoSession()
        new_instance = ContractTx(tx_id=tx_id,
                                asset=asset,address_from=address_from,
                                address_to=address_to,value=value,
                                block_timestamp=block_timestamp,block_height=block_height)
        session.add(new_instance)
        try:
            session.commit()
        except Exception as e:
            logger.error("store contract tx error > txid:{},addressFrom:{},addressTo:{},value:{}\n{}".format(tx_id, address_from, address_to, value,e))
            session.rollback()
        finally:
            session.close()




AccountInfoBase.metadata.create_all(account_info_engine)
