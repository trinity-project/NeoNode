#!/usr/bin/env python
# encoding: utf-8
import json

from app import db

class Token(db.Model):
    __tablename__ = 'token'
    id = db.Column(db.Integer, primary_key=True)
    address = db.Column(db.String(66),unique=True)
    name = db.Column(db.String(32),index=True)
    symbol = db.Column(db.String(8),index=True)
    decimal = db.Column(db.String(2))
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


    def toJson(self):
        return {
            "tokenAddress":self.address,
            "tokenName":self.name,
            "tokenSynbol":self.symbol,
            "tokenDecimal":self.decimal if self.decimal else "0",
            "tokenIcon":self.icon,
            "tokenType":self.token_type

            }

class Utxo(db.Model):
    __tablename__ = 'utxo'
    id = db.Column(db.Integer, primary_key=True)
    tx_id = db.Column(db.String(66))
    vout_number = db.Column(db.String(6))
    address = db.Column(db.String(40),index=True)
    asset_id = db.Column(db.String(66))
    value = db.Column(db.String(16))
    start_block = db.Column(db.Integer)
    end_block = db.Column(db.Integer)
    is_used = db.Column(db.Boolean,default=False)
    is_claimed = db.Column(db.Boolean,default=False)
    gen_gas = db.Column(db.String(16))


    def to_json(self):
        return {
            "txid":self.tx_id,
            "unclaimed":self.gen_gas,
            "n":int(self.vout_number),
            "start_height":self.start_block,
            "end_height":self.end_block,
            "value":int(self.value)
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
    block_timestamp=db.Column(db.Integer)
    block_height=db.Column(db.Integer)




    def to_json(self):
        return {
            "txId":self.tx_id,
            "asset":self.contract,
            "addressFrom":self.address_from,
            "addressTo":self.address_to,
            "value":str(self.value),
            "txReceiptStatus":"1" if "HALT" in self.vm_state else "-1",
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
            "value":self.value,
            "blockTime":self.block_timestamp,
            "blockNumber":self.block_height
        }

class ClaimTx(db.Model):
    __tablename__ = 'claim_tx'
    id = db.Column(db.Integer, primary_key=True)
    tx_id = db.Column(db.String(66))
    address_to = db.Column(db.String(40),index=True)
    value = db.Column(db.String(30))
    block_timestamp=db.Column(db.Integer)



    def to_json(self):
        return {
            "txId":self.tx_id,
            "addressTo":self.address_to,
            "value":self.value,
            "blockTime":self.block_timestamp,
        }

class TokenHolding(db.Model):
    __tablename__ = 'token_holding'
    id = db.Column(db.Integer, primary_key=True)
    contract = db.Column(db.String(42))
    address = db.Column(db.String(40),index=True)


    @staticmethod
    def query_token_holding(address):
        exist_instance = TokenHolding.query.filter(TokenHolding.address == address).all()
        return exist_instance

class ContractTxMapping(db.Model):
    __tablename__ = 'contract_tx_mapping'
    id = db.Column(db.Integer, primary_key=True)
    tx_id = db.Column(db.String(66))
    asset = db.Column(db.String(66))
    address = db.Column(db.String(40),index=True)
    block_height = db.Column(db.Integer)

class Sysfee(db.Model):
    __tablename__ = 'sysfee'
    id = db.Column(db.Integer, primary_key=True)
    sys_fee = db.Column(db.String(16))
    block_height = db.Column(db.Integer,unique=True)

    @staticmethod
    def query_sysfee(block_height):
        exist_instance = Sysfee.query.filter(Sysfee.block_height == block_height).first()
        return exist_instance.sys_fee

class BookmarkForUtxo(db.Model):
    __tablename__ = 'bookmark_for_utxo'
    id = db.Column(db.Integer, primary_key=True)
    height = db.Column(db.Integer)


    @staticmethod
    def query_bookmark_for_utxo():
        exist_instance = BookmarkForUtxo.query.first()
        return exist_instance.height

class ContractTxDetail(db.Model):
    __tablename__ = 'contract_tx_detail'
    id = db.Column(db.Integer, primary_key=True)
    tx_id = db.Column(db.String(66),unique=True)
    inputs = db.Column(db.Text)
    outputs = db.Column(db.Text)
    block_timestamp = db.Column(db.Integer)
    block_height = db.Column(db.Integer)



    def to_json(self):
        return {
            "txId":self.tx_id,
            "inputs":json.loads(self.inputs),
            "outputs":json.loads(self.outputs),
            "blockTime":self.block_timestamp,
            "blockNumber":self.block_height
        }