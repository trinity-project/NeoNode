import binascii
import pymysql
from neocore.Cryptography.Crypto import Crypto
from neocore.UInt160 import UInt160


class TRANSACTION_TYPE(object):
    CONTRACT="ContractTransaction"
    CLAIM="ClaimTransaction"
    INVOKECONTRACT="InvocationTransaction"

def check_database(host,user,passwd,database_name):
    pymysql.install_as_MySQLdb()
    conn = pymysql.connect(host=host, user=user,
                           passwd=passwd)
    cursor = conn.cursor()
    cursor.execute("""create database if not exists {} """.format(database_name))
    cursor.close()
    conn.commit()
    conn.close()


def hex2address(input):
    try:
        output = Crypto.ToAddress(UInt160(data=binascii.unhexlify(bytearray(input.encode("utf8")))))
    except:
        output = None
    return output