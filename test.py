# -*- coding:utf-8 -*-

import datetime
from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session

engine = create_engine("mysql+pymysql://root:root@10.213.87.111:3306/test", echo=True)

# 必须使用scoped_session，域session可以将session进行共享
DBSession = scoped_session(sessionmaker(bind=engine))

BaseModel = declarative_base()


# ----------- Relation Model Object---------------- #

class User(BaseModel):

    __tablename__ = "user"

    id = Column(Integer, primary_key=True)
    name = Column(String)


class UserCredits(BaseModel):

    __tablename__ = "user_credits"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer)
    user_name = Column(String)
    score = Column(Integer)

# ----------- Service implements---------------- #


def add_user(user):
    " 添加用户 "
    session = DBSession()
    try:
        session.add(user)
        # session.commit()
    except Exception as e:
        session.rollback()
        print("AddUser: ======={}=======".format(e))
    # finally:
    #     if not session:
    #         session.close()


def add_user_credits(userCredits, interrupt=True):
    " 添加用户积分记录 "
    session = DBSession()
    try:
        if interrupt:
            raise Exception("--- interrupt ---")

        session.add(userCredits)
        session.commit()
    except Exception as e:
        session.rollback()
        print("AddUserCredits: ======={}=======".format(e))
    finally:
        if not session:
            session.close()


def regist_user():

    session = DBSession()
    try:
        # 开启子事务
        tran=engine.begin()

        # TODO Service
        user_1 = User(name='a')
        user_2 = User(name='b')
        user_3 = User(name='b')
        user_4 = User(name='b')
        add_user(user_1)
        # add_user_credits(UserCredits(
        #     user_id=3,
        #     user_name="ff",
        #     score=10
        # ), False)

        add_user(user_2)
        add_user(user_3)
        add_user(user_4)
        # add_user_credits(UserCredits(
        #     user_id=user_2.id,
        #     user_name=user_2.name,
        #     score=10
        # ), False)
        tran.commit()
    except Exception as e:
        session.rollback()
        print("AddUserCredits: ======={}=======".format(e))
    finally:
        if not session:
            session.close()

# ---------- exec -----------
regist_user()
