import pymysql
from sqlalchemy import Column, Integer, String, Text, create_engine, SmallInteger, DECIMAL, Index, Boolean, or_,UniqueConstraint
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker

from config import setting
from project_log import setup_mylogger

logger=setup_mylogger(logfile="log/store_account_info.log")

pymysql.install_as_MySQLdb()

account_info_engine = create_engine('mysql://%s:%s@%s/%s' %(setting.MYSQLDATABASE["user"],
                                               setting.MYSQLDATABASE["passwd"],
                                               setting.MYSQLDATABASE["host"],
                                               setting.MYSQLDATABASE["db_account_info"]
                                                            ),
                                   echo=True)

AccountInfoSession = sessionmaker(bind=account_info_engine)
# AccountInfoSession = sessionmaker(bind=account_info_engine)
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
    def query(address,asset_id):
        session=AccountInfoSession()
        exist_instance=session.query(Balance).filter(Balance.address==address,Balance.asset_id==asset_id).first()
        return exist_instance


    @staticmethod
    def update(self):
        session = AccountInfoSession()
        session.add(self)
        try:
            session.commit()
        except:
            session.rollback()
        finally:
            if not session:
                session.close()

    @staticmethod
    def save(address,asset_id,value):
        session=AccountInfoSession()
        new_instance = Balance(address=address,asset_id=asset_id,value=value)
        try:
            session.add(new_instance)
            session.commit()
        except:
            logger.error("balance")
            session.rollback()
        finally:
            if not session:
                session.close()

class LocalBlockCout(AccountInfoBase):
    __tablename__ = 'local_block_count'
    id = Column(Integer, primary_key=True)
    height = Column(Integer)

    @staticmethod
    def query():
        session=AccountInfoSession()
        exist_instance=session.query(LocalBlockCout).first()
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
            if not session:
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
            if not session:
                session.close()



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
    def query(tx_id,vout_number):
        session=AccountInfoSession()
        exist_instance=session.query(Vout).filter(Vout.tx_id==tx_id,
                                                  Vout.vout_number==vout_number).first()
        return exist_instance

    @staticmethod
    def save(tx_id,address,asset_id,vout_number,value):
        # session=AccountInfoSession()
        new_instance = Vout(tx_id=tx_id, address=address, asset_id=asset_id,
                               vout_number=vout_number,value=value)
        try:
            session.add(new_instance)
            session.commit()
        except Exception as e:
            logger.error(e)
            session.rollback()
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
            if not session:
                session.close()

class HandledTx(AccountInfoBase):
    __tablename__ = 'handled_tx'
    id = Column(Integer, primary_key=True)
    tx_id = Column(String(66),unique=True)


    @staticmethod
    def query(tx_id):
        session = AccountInfoSession()
        exist_instance = session.query(HandledTx).filter(HandledTx.tx_id==tx_id).first()
        return exist_instance

    @staticmethod
    def save(tx_id):
        session=AccountInfoSession()
        new_instance = HandledTx(tx_id=tx_id)
        session.add(new_instance)
        try:
            session.commit()
        except Exception as e:
            session.rollback()
        finally:
            if not session:
                session.close()



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
    def query(tx_id,vout_number):
        session=AccountInfoSession()
        exist_instance=session.query(Vin).filter(Vin.tx_id==tx_id,
                                                  Vin.vout_number==vout_number).first()
        return exist_instance

    @staticmethod
    def save(tx_id,address,asset_id,vout_number,value):
        session=AccountInfoSession()
        new_instance = Vin(tx_id=tx_id, address=address, asset_id=asset_id,
                               vout_number=vout_number,value=value)
        try:
            session.add(new_instance)
            # session.commit()
        except Exception as e:
            logger.error("vin")
            # session.rollback()







AccountInfoBase.metadata.create_all(account_info_engine)




session = AccountInfoSession()
try:
    session.begin(subtransactions=True)
    tx_id = "tx1"
    vout_number = "91"

    address = "addr6"
    asset_id = "asset3"
    value = "2"

    vin_txid = "vin_tx11"
    vin_vout_number = "0"

    Vout.save(tx_id=tx_id, address=address, asset_id=asset_id,
              vout_number=vout_number, value=value)

    Vout.save(tx_id=tx_id, address=address, asset_id=asset_id,
              vout_number="92", value=value)


    Vout.save(tx_id=tx_id, address=address, asset_id=asset_id,
              vout_number="93", value=value)




    # Vin.save(vin_txid, "addr", "asset", vin_vout_number, "5")
    # Vin.save(vin_txid, "addr", "asset", "20", "5")
    # Vin.save(vin_txid, "addr", "asset", "21", "5")
    # Balance.save(address, asset_id, value)


    session.commit()
except Exception as e:
    logger.error(e)
    session.rollback()

finally:
    print(session)
    if not session:
        print("not session")
        session.close()