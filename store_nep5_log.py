#!/usr/bin/env python
# coding=utf-8
import json
import os
import binascii
from decimal import Decimal
import time
from neocore.Cryptography.Crypto import Crypto
from neocore.UInt160 import UInt160
from pyinotify import WatchManager, Notifier, ProcessEvent, IN_CREATE
from config import setting
from data_model.store_nep5tx_model import InvokeTx


def hex_reverse(input):
    tmp_list = []
    for i in range(0, len(input), 2):
        tmp_list.append(input[i:i + 2])
    hex_str = "".join(list(reversed(tmp_list)))
    return hex_str

def hex2address(input):
    output = Crypto.ToAddress(UInt160(data=binascii.unhexlify(bytearray(input.encode("utf8")))))


    return output

def hex2interger(input):
    tmp_list = []
    for i in range(0, len(input), 2):
        tmp_list.append(input[i:i + 2])
    hex_str = "".join(list(reversed(tmp_list)))
    output = int(hex_str, 16)

    return output

def read_file(file):
    with open (file,"rb") as f:
        content = f.read().decode()
        return content


class EventHandler(ProcessEvent):
    """事件处理"""

    def process_IN_CREATE(self, event):
        filepath=os.path.join(event.path, event.name)
        time.sleep(0.5)
        content = json.loads(read_file(filepath))
        if not content["notifications"]:
            return
        contract = content["notifications"][0]["contract"]
        tx_id=content["txid"]

        if contract !=setting.CONTRACTHASH:
            return
        address_from=hex2address(content["notifications"][0]["state"]["value"][1]["value"])
        address_to=hex2address(content["notifications"][0]["state"]["value"][2]["value"])
        value=hex2interger(content["notifications"][0]["state"]["value"][3]["value"])
        InvokeTx.save(
                      tx_id=tx_id,contract=contract,address_from=address_from,address_to=address_to,
                      value=Decimal(str(value)),vm_state=content["vmstate"],block_timestamp=int(time.time()))


def FSMonitor(path=""):
    wm = WatchManager()
    mask = IN_CREATE
    notifier = Notifier(wm, EventHandler())
    wm.add_watch(path, mask, auto_add=True, rec=True)

    while True:
        try:
            notifier.process_events()
            if notifier.check_events():
                notifier.read_events()
        except KeyboardInterrupt:
            notifier.stop()
            break


if __name__ == "__main__":

    FSMonitor(setting.APPLICATIONLOGDIR)

