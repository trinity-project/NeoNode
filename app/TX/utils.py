import binascii
from base58 import b58decode
from decimal import Decimal
from neocore.KeyPair import KeyPair
from neocore.UInt160 import UInt160
from neocore.UInt256 import UInt256
from neocore.BigInteger import BigInteger
from neocore.Cryptography.Crypto import Crypto

from config import setting


def str_reverse(input):
    tmp=binascii.unhexlify(input)
    be=bytearray(tmp)
    be.reverse()
    output=binascii.hexlify(be).decode()
    return output


def hex_reverse(input):
    tmp=binascii.unhexlify(input[2:])
    be=bytearray(tmp)
    be.reverse()
    output=binascii.hexlify(be).decode()
    return output


def int_to_hex(input):
    return binascii.hexlify(bytes([int(input)])).decode()


def ToAddresstHash(address):

    data = b58decode(address)
    if len(data) != 25:
        raise ValueError('Not correct Address, wrong length.')
    if data[0] != 23:
        raise ValueError('Not correct Coin Version')

    checksum = Crypto.Default().Hash256(data[:21])[:4]
    if checksum != data[21:]:
        raise Exception('Address format error')
    return UInt160(data=data[1:21])


def pubkeyToAddress(pubkey):
    pubkey = "21" + pubkey + "ac"
    sc =pubkey.encode()
    address=Crypto.ToAddress(Crypto.ToScriptHash(sc))
    return address

def pubkeyToAddressHash(pubkey):
    pubkey="21"+pubkey+"ac"
    sc =pubkey.encode()
    sc_hash=Crypto.ToScriptHash(sc).ToString2()
    return sc_hash

def createVerifyScript(script):
    tmp = hex(int(len(script)/2))[2:]
    if len(tmp) % 2 == 1:
        tmp = "0" + tmp
    be=bytearray (binascii.unhexlify(tmp))
    be.reverse()
    hex_len=binascii.hexlify(be).decode()
    verify_script="".join([hex_len, script])
    return verify_script

def createTxid(txData):
    ba = binascii.unhexlify(txData)
    hash = Crypto.Hash256(ba)
    return "0x"+UInt256(data=hash).ToString()


def createMultiSigAddress(script):
    scriptHash=Crypto.ToScriptHash(script)
    address=Crypto.ToAddress(scriptHash)
    return address

def create_opdata(address_from, address_to, value, contract_hash):
    op_data = ""
    value=int(value)
    value = binascii.hexlify(BigInteger(value).ToByteArray()).decode()
    scripthash_from = ToAddresstHash(address_from).ToString2()
    scripthash_to = ToAddresstHash(address_to).ToString2()
    method = binascii.hexlify("transfer".encode()).decode()
    invoke_args = [value, scripthash_to, scripthash_from]
    for item in invoke_args:
        op_data += "".join([int_to_hex(len(item) / 2), item])

    op_data += "53"  # PUSH3
    op_data += "c1"  # PACK
    op_data += int_to_hex(len(method) / 2)
    op_data += method
    op_data += "67"  # APPCALL
    op_data += hex_reverse(contract_hash)
    op_data += "f1"  # maybe THROWIFNOT

    return op_data



def createRSMCContract(hashSelf,pubkeySelf,hashOther,pubkeyOther,magicTimestamp):
    magicTimestamp = binascii.hexlify(str(magicTimestamp).encode()).decode()
    length=hex(int(len(magicTimestamp)/2))[2:]
    magicTimestamp=length+magicTimestamp
    contractTemplate="5dc56b6c766b00527ac46c766b51527ac46c766b52527ac461{magicTimestamp}6c766b53527ac4616829537" \
                     "97374656d2e457865637574696f6e456e67696e652e476574536372697074436f6e7461696e65726c766b5452" \
                     "7ac46c766b54c361681d4e656f2e5472616e73616374696f6e2e476574417474726962757465736c766b55527" \
                     "ac4616c766b55c36c766b56527ac4006c766b57527ac462b4016c766b56c36c766b57c3c36c766b58527ac461" \
                     "6c766b58c36168154e656f2e4174747269627574652e476574446174616114{hashOther}9c6c766b59527ac4" \
                     "6c766b59c364c300616c766b00c36121{pubkeySelf}ac642f006c766b51c36121{pubkeyOther}ac635f006c" \
                     "766b00c36121{pubkeyOther}ac642f006c766b51c36121{pubkeySelf}ac62040000620400516c766b5a527a" \
                     "c462b8006c766b58c36168154e656f2e4174747269627574652e476574446174616114{hashSelf}9c6c766b5" \
                     "b527ac46c766b5bc3644c00616c766b52c36c766b54c3617c6599016c766b5c527ac46c766b5cc36422006c76" \
                     "6b52c36c766b00c36c766b51c3615272654a006c766b5a527ac4623700006c766b5a527ac4622c00616c766b5" \
                     "7c351936c766b57527ac46c766b57c36c766b56c3c09f6343fe006c766b5a527ac46203006c766b5ac3616c75" \
                     "6656c56b6c766b00527ac46c766b51527ac46c766b52527ac4616168184e656f2e426c6f636b636861696e2e4" \
                     "765744865696768746c766b53527ac46c766b00c3011e936c766b53c39f6c766b54527ac46c766b54c364c200" \
                     "6c766b51c36121{pubkeySelf}ac642f006c766b52c36121{pubkeyOther}ac635f006c766b51c36121" \
                     "{pubkeyOther}ac642f006c766b52c36121{pubkeySelf}ac62040000620400516c766b55527ac4620e00006c" \
                     "766b55527ac46203006c766b55c3616c75665ec56b6c766b00527ac46c766b51527ac4616c766b00c36168174" \
                     "e656f2e426c6f636b636861696e2e476574426c6f636b6c766b52527ac46c766b52c36168194e656f2e426c6f" \
                     "636b2e4765745472616e73616374696f6e736c766b53527ac46c766b51c361681d4e656f2e5472616e7361637" \
                     "4696f6e2e476574417474726962757465736c766b54527ac4616c766b54c36c766b55527ac4006c766b56527a" \
                     "c462d1006c766b55c36c766b56c3c36c766b57527ac4616c766b57c36168154e656f2e4174747269627574652" \
                     "e476574446174616c766b58527ac4616c766b53c36c766b59527ac4006c766b5a527ac46264006c766b59c36c" \
                     "766b5ac3c36c766b5b527ac4616c766b5bc36168174e656f2e5472616e73616374696f6e2e476574486173686" \
                     "c766b58c39c6c766b5c527ac46c766b5cc3640e00516c766b5d527ac4624a00616c766b5ac351936c766b5a52" \
                     "7ac46c766b5ac36c766b59c3c09f6393ff616c766b56c351936c766b56527ac46c766b56c36c766b55c3c09f6" \
                     "326ff006c766b5d527ac46203006c766b5dc3616c7566"
    RSMCContract=contractTemplate.format(hashOther=hashOther,pubkeySelf=pubkeySelf,hashSelf=hashSelf,
                                         pubkeyOther=pubkeyOther,magicTimestamp=magicTimestamp)

    return  {
        "script":RSMCContract,
        "address":createMultiSigAddress(RSMCContract)
    }




def createHTLCContract(futureTimestamp,pubkeySelf,pubkeyOther,hashR):
    futureTimestamp=hex_reverse(hex(int(futureTimestamp)))
    contractTemplate="58c56b6c766b00527ac46c766b51527ac46c766b52527ac4616c766b52c3a76c766b53527ac46168184e656f2e4" \
                     "26c6f636b636861696e2e4765744865696768746168184e656f2e426c6f636b636861696e2e4765744865616465" \
                     "726c766b54527ac46c766b00c36121{pubkeyA}ac642f006c766b51c36121{pubkeyB}ac635f006c766b00c3612" \
                     "1{pubkeyB}ac642f006c766b51c36121{pubkeyA}ac62040000620400516c766b55527ac46c766b54c36168174e" \
                     "656f2e4865616465722e47657454696d657374616d7004{futureTimestamp}9f6c766b56527ac46c766b56c364" \
                     "3600616c766b55c36422006c766b53c36114{hashR}9c620400006c766b57527ac46212006c766b55c36c766b57" \
                     "527ac46203006c766b57c3616c7566"

    HTLCContract=contractTemplate.format(futureTimestamp=futureTimestamp,pubkeyA=pubkeySelf,pubkeyB=pubkeyOther,hashR=hashR)


    return  {
        "script":HTLCContract,
        "address":createMultiSigAddress(HTLCContract)
    }



def createMultiSigContract(pubkeySelf,pubkeyOther):
    pubkey_large = max(pubkeySelf,pubkeyOther)
    pubkey_small = min(pubkeySelf,pubkeyOther)

    contractTemplate = "53c56b6c766b00527ac46c766b51527ac4616c766b00c36121{pubkeySelf}ac642f006c766b51c361" \
                       "21{pubkeyOther}ac635f006c766b00c36121{pubkeyOther}ac642f006c766b51c36121{pubkeySelf}" \
                       "ac62040000620400516c766b52527ac46203006c766b52c3616c7566"

    script=contractTemplate.format(pubkeySelf=pubkey_small,pubkeyOther=pubkey_large)
    address=createMultiSigAddress(script)


    return {
        "script":script,
        "address":address
    }

def blockheight_to_script(input):
    input=hex(input)[2:]

    if len(input) % 2 == 1:
        input = "0" + input
    be=bytearray (binascii.unhexlify(input))
    be.reverse()
    revese_hex=binascii.hexlify(be).decode()
    revese_hex_len=binascii.hexlify(bytes([int(len(revese_hex)/2)])).decode()
    len_all=str(83+int(revese_hex_len))
    output="".join([len_all,revese_hex_len, revese_hex])
    return output


def R_to_script(input):

    hex_R=binascii.hexlify(input.encode()).decode()
    hex_R_len=binascii.hexlify(bytes([int(len(hex_R)/2)])).decode()

    len_all="c3"
    output="".join([len_all,hex_R_len, hex_R])
    return output

def privtkey_sign(txData,privteKey):
    return binascii.hexlify(Crypto.Sign(message=txData, private_key=privteKey)).decode()

def privtKey_to_publicKey(privtKey):

    pk=binascii.unhexlify(privtKey)
    keypair = KeyPair(pk)
    vk=keypair.PublicKey.encode_point(True).decode()
    return vk


def sign(txData,privtKey):
    signature = privtkey_sign(txData,privtKey)
    publicKey=privtKey_to_publicKey(privtKey)
    rawData=txData+"01"+"41"+"40"+signature+"23"+"21"+publicKey+"ac"
    return rawData


def get_vout_by_address(address,value,assetId):
    inputs_total=0
    inputs=[]
    if assetId == setting.GAS_ASSETID or assetId == setting.NEO_ASSETID:
        vouts = Vout.query.filter_by(address=address,asset_id=assetId).order_by(Vout.value.desc()).all()

        for item in vouts:
            if float(item.value) >= value:
                input =(item.tx_id,item.value,item.vout_number)
                inputs.append(input)
                inputs_total+=float(item.value)
                return inputs,inputs_total
            else:
                input = (item.tx_id, item.value, item.vout_number)
                inputs.append(input)
                inputs_total+=float(item.value)
                if inputs_total>=value:
                    return inputs,inputs_total

    return inputs,inputs_total

