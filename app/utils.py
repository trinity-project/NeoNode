import binascii

import requests
from base58 import b58decode
from decimal import Decimal
from neocore.Cryptography.Crypto import Crypto
from neocore.UInt160 import UInt160
from neocore.BigInteger import BigInteger
from neocore.KeyPair import KeyPair
from neocore.UInt256 import UInt256

from app.model import Sysfee
from config import setting


def createMultiSigAddress(script):
    scriptHash=Crypto.ToScriptHash(script)
    address=Crypto.ToAddress(scriptHash)
    return address


def ToScriptHash(address):
    data = b58decode(address)
    if len(data) != 25:
        raise ValueError('Not correct Address, wrong length.')
    if data[0] != 23:
        raise ValueError('Not correct Coin Version')

    checksum = Crypto.Default().Hash256(data[:21])[:4]
    if checksum != data[21:]:
        raise Exception('Address format error')
    return UInt160(data=data[1:21])


def hex_reverse(input):
    tmp_list = []
    for i in range(0, len(input), 2):
        tmp_list.append(input[i:i + 2])
    hex_str = "".join(list(reversed(tmp_list)))
    return hex_str


def int_to_hex(input):
    return binascii.hexlify(bytes([int(input)])).decode()


def privtkey_sign(txData,privteKey):
    signature=binascii.hexlify(Crypto.Sign(message=txData, private_key=privteKey)).decode()
    return signature



def construct_opdata(addressFrom,addressTo,value,assetId):
    op_data=""
    value=binascii.hexlify(BigInteger(value*pow(10,8)).ToByteArray()).decode()
    scripthash_from=ToScriptHash(addressFrom).ToString2()
    scripthash_to=ToScriptHash(addressTo).ToString2()
    method=binascii.hexlify("transfer".encode()).decode()
    invoke_args=[value,scripthash_to,scripthash_from]
    for item in invoke_args:
        op_data+="".join([int_to_hex(len(item)/2),item])

    op_data+="53"     #PUSH3
    op_data+="c1"     #PACK
    op_data+=int_to_hex(len(method)/2)
    op_data+=method
    op_data+="67"                      #APPCALL
    op_data+=hex_reverse(assetId)
    op_data+= "f1"                      # maybe THROWIFNOT

    return op_data






def privtKey_to_publicKey(privtKey):

    pk=binascii.unhexlify(privtKey)
    keypair = KeyPair(pk)
    vk=keypair.PublicKey.encode_point(True).decode()
    return vk


def createTxid(txData):
    ba = binascii.unhexlify(txData)
    hash = Crypto.Hash256(ba)
    return UInt256(data=hash).ToString()


def verify_password(password, hashed):
    import bcrypt
    if isinstance(password, str):
        password = password.encode("utf-8")
    if isinstance(hashed, str):
        hashed = hashed.encode("utf-8")
    try:
        result = bcrypt.checkpw(password, hashed)
    except Exception:
        result = False
    return result


def get_claimable_from_neoscan(address):
    try:
        res = requests.get(setting.NEO_SCAN_API + "/get_claimable/" + address).json()
        return res.get("unclaimed"),res.get("claimable")
    except Exception as e:
        raise e


def get_unclaimed_from_neoscan(address):
    try:
        res = requests.get(setting.NEO_SCAN_API + "/get_unclaimed/" + address).json()
        return res.get("unclaimed")
    except Exception as e:
        raise e

def get_tokenholding_from_neoscan(address):
    try:
        res = requests.get(setting.NEO_SCAN_API + "/get_balance/" + address).json()
        return res.get("balance")
    except Exception as e:
        raise e

def handle_invoke_tx_decimal(tx,decimal):
    if tx.get("value"):
        tx["value"] = str(Decimal(tx["value"]) / (10 ** decimal))
    return tx


#以1个NEO计算
def count_block_reward_gas(start_block,end_block):
    step = 2000000
    block_reward = 8
    gas_count = 0
    for i in range(22):
        start = i * step
        end = (i+1) * step -1
        if end_block < start:
            break
        if start_block <= end:
            if start_block > start:
                start = start_block
            if end_block < end:
                end = end_block
            gas_count += (end - start) * block_reward

        if block_reward > 1:
            block_reward -= 1
    return Decimal(gas_count)/pow(10,8)

#以1个NEO计算
def count_sysfee_gas(start_block,end_block):
    total_sysfee_start = Sysfee.query_sysfee(start_block)
    total_sysfee_end = Sysfee.query_sysfee(end_block)
    diffence_fee = Decimal(total_sysfee_end) - Decimal(total_sysfee_start)
    return diffence_fee/pow(10,8)

def cul_gas(neo_amount,start_block,end_block):

    g1= count_block_reward_gas(start_block,end_block)
    g2 = count_sysfee_gas(start_block,end_block)

    return str((g1+g2)*neo_amount)