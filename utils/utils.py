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


def hex_reverse(input):
    tmp_list = []
    for i in range(0, len(input), 2):
        tmp_list.append(input[i:i + 2])
    hex_str = "".join(list(reversed(tmp_list)))
    return hex_str


def hex2interger(input):
    try:
        tmp_list = []
        for i in range(0, len(input), 2):
            tmp_list.append(input[i:i + 2])
        hex_str = "".join(list(reversed(tmp_list)))
        output = int(hex_str, 16)

        return output
    except:
        return None