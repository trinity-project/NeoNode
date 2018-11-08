import pymysql, json

def insert_block_info(tx_id,tx_type,block_height,block_time,vin,vout,script):
    connection = pymysql.connect(host='127.0.0.1',
                                 port=3306,
                                 user='root',
                                 password='maiganne378121',
                                 db='block_info',
                                 charset='utf8mb4',
                                 cursorclass=pymysql.cursors.DictCursor)

    with connection.cursor() as cursor:
        sql = 'insert into tx (tx_id,tx_type,block_height,block_time,vin,vout,script) values (%s,%s,%s,%s,%s,%s,%s)'

        cursor.execute(sql, (tx_id,tx_type,block_height,block_time,json.dumps(vin),json.dumps(vout),script))
        connection.commit()
        connection.close()


def insert_vout(tx_id,address,asset_id,vout_number,value):
    connection = pymysql.connect(host='127.0.0.1',
                                 port=3306,
                                 user='root',
                                 password='maiganne378121',
                                 db='neo_table',
                                 charset='utf8mb4',
                                 cursorclass=pymysql.cursors.DictCursor)

    with connection.cursor() as cursor:
        sql = 'insert into vout (tx_id,address,asset_id,vout_number,value) values (%s,%s,%s,%s,%s)'

        cursor.execute(sql, (tx_id,address,asset_id,vout_number,value))
        connection.commit()
        connection.close()


insert_block_info(tx_id="0xc4edefaf13a98d8942a6bce8230d14b80e1b162081e938981810abdb563ee824",
                  tx_type="MinerTransaction",
                  block_height=670878,
                  block_time=1489988232,
                  vin = [],
                  vout = [
            {
                "n": 0,
                "asset": "0x602c79718b16e442de58778e148d0b1084e3b2dffd5de6b7b16cee7969282de7",
                "value": "10000",
                "address": "AJeAEsmeD6t279Dx4n2HWdUvUmmXQ4iJvP"
            }
        ],
                  script=None
                  )


insert_vout(tx_id="0xc4edefaf13a98d8942a6bce8230d14b80e1b162081e938981810abdb563ee824",
            address="AJeAEsmeD6t279Dx4n2HWdUvUmmXQ4iJvP",
            asset_id="0x602c79718b16e442de58778e148d0b1084e3b2dffd5de6b7b16cee7969282de7",
            vout_number="0",
            value="10000"
            )