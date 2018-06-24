#!/usr/bin/env python
# coding=utf-8

import time
import requests
from config import setting
from data_model.account_info_model import InvokeTx

from project_log import setup_mylogger

logger=setup_mylogger("log/push_transfer_info.log")




def push_transfer(txId,addressFrom,addressTo,value,blockTimestamp):
    headers={
        "Password":"!QWWpigxo1970q~"
    }
    data = {
        "txId":txId,
        "addressFrom": addressFrom,
        "addressTo": addressTo,
        "value": str(value),
        "blockTimestamp":blockTimestamp
    }
    try:
        res = requests.post(setting.WEBAPI, json=data,headers=headers).json()
        return res["Code"]
    except Exception:
        return None
def TransferMonitor():


    while True:
        exist_instance = InvokeTx.query()
        if exist_instance:

            res=push_transfer(exist_instance.tx_id,exist_instance.address_from,
                              exist_instance.address_to,exist_instance.value,int(time.time()))
            if res==0:
                exist_instance.has_pushed=1
                logger.info("push tx:{} sucess addressFrom:{},addressTo:{},value:{}".format(exist_instance.tx_id,exist_instance.address_from,
                                                                                            exist_instance.address_to,exist_instance.value))
                InvokeTx.update(exist_instance)
            else:
                logger.error("push tx:{} falil addressFrom:{},addressTo:{},value:{}".format(exist_instance.tx_id,exist_instance.address_from,
                                                                                            exist_instance.address_to,exist_instance.value))
                time.sleep(3)
        else:
            time.sleep(10)

if __name__ == "__main__":
    TransferMonitor()