#!/usr/bin/env python
# encoding: utf-8
"""
@author: Maiganne

"""


from app import db




class Balance(db.Model):
    __tablename__ = 'balance'
    id = db.Column(db.Integer, primary_key=True)
    address = db.Column(db.String(40),index=True)
    neo_balance = db.Column(db.DECIMAL(17,8),default=0)
    gas_balance =db.Column(db.DECIMAL(17,8),default=0)






class Vout(db.Model):
    __tablename__ = 'vout'
    id = db.Column(db.Integer, primary_key=True)
    tx_id = db.Column(db.String(66),index=True)
    address = db.Column(db.String(40))
    asset_id = db.Column(db.String(66))
    vout_number = db.Column(db.SmallInteger)
    value = db.Column(db.DECIMAL(17,8))




class Token(db.Model):
    __tablename__ = 'token'
    id = db.Column(db.Integer, primary_key=True)
    address = db.Column(db.String(42),unique=True)
    name = db.Column(db.String(64),index=True)
    symbol = db.Column(db.String(64),index=True)
    decimal = db.Column(db.String(64))
    token_type = db.Column(db.String(8))
    chain_type = db.Column(db.String(8))
    icon = db.Column(db.String(256))

    @staticmethod
    def query_token(address=None,symbol=None):
        exist_instance = None

        if address:

            exist_instance = Token.query.filter(Token.address==address).first()


        if symbol:
            exist_instance = Token.query.filter(Token.symbol == symbol).first()


        return exist_instance


    @staticmethod
    def save(address,name,symbol,decimal,tokenType,chainType,icon):
        new_instance = Token(address=address, name=name,symbol=symbol,decimal=decimal,
                             token_type = tokenType,chain_type=chainType,icon=icon)
        db.session.add(new_instance)
        try:
            db.session.commit()
            return True
        except Exception as e:
            return False



    def toJson(self):
        return {
            "tokenAddress":self.address,
            "tokenName":self.name,
            "tokenSynbol":self.symbol,
            "tokenDecimal":self.decimal,
            "tokenIcon":self.icon,
            "tokenType":self.token_type

            }



class InvokeTx(db.Model):
    __tablename__ = 'invoke_tx'
    id = db.Column(db.Integer, primary_key=True)
    tx_id = db.Column(db.String(66))
    contract = db.Column(db.String(42))
    address_from = db.Column(db.String(40),index=True)
    address_to = db.Column(db.String(40),index=True)
    value = db.Column(db.DECIMAL(17,8))
    vm_state = db.Column(db.String(16))
    has_pushed=db.Column(db.Boolean,default=False)
    block_timestamp=db.Column(db.Integer)
    block_height=db.Column(db.Integer)




    def to_json(self):
        return {
            "txId":self.tx_id,
            "asset":self.contract,
            "addressFrom":self.address_from,
            "addressTo":self.address_to,
            "value":str(float(self.value)),
            "txReceiptStatus":"1" if self.vm_state=="HALT, BREAK" else "-1",
            "blockTime":self.block_timestamp,
            "blockNumber":self.block_height
        }


class ContractTx(db.Model):
    __tablename__ = 'contract_tx'
    id = db.Column(db.Integer, primary_key=True)
    tx_id = db.Column(db.String(66))
    asset = db.Column(db.String(66))
    address_from = db.Column(db.String(40),index=True)
    address_to = db.Column(db.String(40),index=True)
    value = db.Column(db.DECIMAL(17,8))
    block_timestamp=db.Column(db.Integer)
    block_height=db.Column(db.Integer)

    def to_json(self):
        return {
            "txId":self.tx_id,
            "asset":self.asset,
            "addressFrom":self.address_from,
            "addressTo":self.address_to,
            "value":str(float(self.value)),
            "blockTime":self.block_timestamp,
            "blockNumber":self.block_height
        }