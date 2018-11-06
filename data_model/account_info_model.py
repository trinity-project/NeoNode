import pymysql

from sqlalchemy.dialects.mysql import LONGTEXT
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Text, create_engine,UniqueConstraint
from sqlalchemy.orm import sessionmaker

from config import setting
from project_log import setup_mylogger

logger=setup_mylogger(logfile="log/store_account_info.log")




pymysql.install_as_MySQLdb()

def _check_database(database_name):
    conn = pymysql.connect(host=setting.MYSQLDATABASE["host"], user=setting.MYSQLDATABASE["user"],
                           passwd=setting.MYSQLDATABASE["passwd"])
    cursor = conn.cursor()
    cursor.execute("""CREATE DATABASE IF NOT EXISTS {} DEFAULT CHARSET utf8 COLLATE utf8_general_ci;""".format(database_name))
    cursor.close()
    conn.commit()
    conn.close()


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
    address = Column(String(40))
    asset_id = Column(String(66))
    value =Column(String(30))

    __table_args__ = (
        UniqueConstraint('address', 'asset_id'),
    )

    @staticmethod
    def query(session,address,asset_id):
        exist_instance=session.query(Balance).filter(Balance.address==address,Balance.asset_id==asset_id).first()
        return exist_instance




    @staticmethod
    def save(session,address,asset_id,value):
        new_instance = Balance(address=address,asset_id=asset_id,value=value)
        session.begin(subtransactions=True)
        try:
            session.add(new_instance)
            session.commit()
        except Exception as e:
            logger.error(e)
            session.rollback()

    # @staticmethod
    # def update(session,exist_instance):
    #     session.add(exist_instance)
    #     # session.flush()


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
    address = Column(String(40))
    asset_id = Column(String(66))
    vout_number = Column(String(6))
    value = Column(String(30))

    __table_args__ = (
        UniqueConstraint('tx_id', 'vout_number'),
    )


    @staticmethod
    def query(session,tx_id,vout_number):
        exist_instance=session.query(Vout).filter(Vout.tx_id==tx_id,
                                                  Vout.vout_number==vout_number).first()
        return exist_instance

    @staticmethod
    def save(session,tx_id,address,asset_id,vout_number,value):
        new_instance = Vout(tx_id=tx_id, address=address, asset_id=asset_id,
                               vout_number=vout_number,value=value)

        session.begin(subtransactions=True)
        try:
            session.add(new_instance)
            session.commit()
        except Exception as e:
            logger.error(e)
            session.rollback()


    @staticmethod
    def delete(session,instanse):
        session.delete(instanse)


class HandledTx(AccountInfoBase):
    __tablename__ = 'handled_tx'
    id = Column(Integer, primary_key=True)
    tx_id = Column(String(66),unique=True)


    @staticmethod
    def query(session,tx_id):
        exist_instance = session.query(HandledTx).filter(HandledTx.tx_id==tx_id).first()
        return exist_instance

    @staticmethod
    def save(session,tx_id):
        new_instance = HandledTx(tx_id=tx_id)
        session.begin(subtransactions=True)
        try:
            session.add(new_instance)
            session.commit()
        except Exception as e:
            logger.error(e)
            session.rollback()




class Vin(AccountInfoBase):
    __tablename__ = 'vin'
    id = Column(Integer, primary_key=True)
    tx_id = Column(String(66))
    vout_number = Column(String(6))
    address = Column(String(40))
    asset_id = Column(String(66))
    value = Column(String(30))

    __table_args__ = (
        UniqueConstraint('tx_id', 'vout_number'),
    )


    @staticmethod
    def query(session,tx_id,vout_number):
        exist_instance=session.query(Vin).filter(Vin.tx_id==tx_id,
                                                  Vin.vout_number==vout_number).first()
        return exist_instance

    @staticmethod
    def save(session,tx_id,address,asset_id,vout_number,value):
        new_instance = Vin(tx_id=tx_id, address=address, asset_id=asset_id,
                               vout_number=vout_number,value=value)
        session.begin(subtransactions=True)
        try:
            session.add(new_instance)
            session.commit()
        except Exception as e:
            logger.error(e)
            session.rollback()



class InvokeTx(AccountInfoBase):
    __tablename__ = 'invoke_tx'
    id = Column(Integer, primary_key=True)
    tx_id = Column(String(66),unique=True)
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
                                block_timestamp=block_timestamp,block_height=block_height)
        session.add(new_instance)





class ContractTx(AccountInfoBase):
    __tablename__ = 'contract_tx'
    id = Column(Integer, primary_key=True)
    tx_id = Column(String(66))
    asset = Column(String(66))
    address_from = Column(String(40),index=True)
    address_to = Column(String(40),index=True)
    value = Column(String(30))
    block_timestamp=Column(Integer)
    block_height=Column(Integer)



    @staticmethod
    def save(session,tx_id,asset,address_from,address_to,value,block_timestamp,block_height):
        new_instance = ContractTx(tx_id=tx_id,
                                asset=asset,address_from=address_from,
                                address_to=address_to,value=value,
                                block_timestamp=block_timestamp,block_height=block_height)
        session.add(new_instance)





AccountInfoBase.metadata.create_all(account_info_engine)
