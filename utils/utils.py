import pymysql


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