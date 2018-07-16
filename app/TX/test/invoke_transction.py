import binascii
import time
from neocore.BigInteger import BigInteger
from neocore.Cryptography.Crypto import Crypto

from TX.adapter.tnc_factory import createFundingTx

walletSelf= {
    "pubkey": "0338f92d2dbb3a5ff1f2bd47b5aefdcd61020525b2f6d6e0bb524f5ea8c88cea19",
    "address": "AZgssA2LbcFfsrba5WsKx3Rzx1wmVqpb6r",
    "deposit": 1


}
walletOther= {

    "pubkey": "026f0eaeed68e9b630bf5541d05aef78330403349bd6a3ad5567fcbc689ff7c414",
    "address": "AMxCb9gDqwC6hhP1D4G4ERy8FWtavvVkEb",
    "deposit": 1
}






#
# HC_tx =createHCTX(pubkeySelf="03ed45d1fdf6dbd5a6e5567b50d2b36b8ae5c1cd0123f26aba000fd3a72d6fbd28",
#                   pubkeyOther="03d8f667ff2068751e117cd6dbe3ebe286dbbc7fbb7b1ef0fbf5eb068e8b783a94",
#                   addressSelf="ASm37KDVtgNQRqd4eefYGKCGn8fQH3mHw2",addressOther="AJAd9ZaZCwLvdktHc1Rs7w3hmpVSBuTKzs",
#                   HTLCValue=5,balanceSelf=10,
#                   balanceOther=10,hashR="7c4a8d09ca3762af61e59520943dc26494f8941b",
#                   addressFunding="AQmhy9TH8jVjz8YyBzFSQ2yhGcPAKUd96N")





funding_tx = createFundingTx(walletSelf=walletSelf,walletOther=walletOther,asset_id= "0x0c34a8fd0109df360c7cf7ca454404901db77f5e")
print(funding_tx)

# C_tx = createCTX(addressFunding=funding_tx["addressFunding"],addressSelf=walletSelf["address"],
#                  balanceSelf=walletSelf["deposit"],addressOther=walletOther["address"],
#                  balanceOther=walletOther["deposit"],pubkeySelf=walletSelf["pubkey"],pubkeyOther=walletOther["pubkey"])
#
# RD_tx = createRDTX(addressRSMC= C_tx["addressRSMC"],addressSelf=walletSelf["address"],
#                    balanceSelf=walletSelf["deposit"],CTxId=C_tx["txId"])
#
# BR_tx = createBRTX(addressRSMC=C_tx["addressRSMC"],addressOther=walletOther["address"],balanceSelf=walletSelf["deposit"])
# BR_tx = createBRTX(addressRSMC="AJJFzQuAtFaLjW2bLEiuDdY682USNswKhC",addressOther=walletOther["address"],balanceSelf=walletSelf["deposit"])



# xx=createRD1ATX(addressA1B="AQfnZ3euLYqaEhdeTEqqqeQVtWYTtFHzFx",addressA="ALcC96eesqb9pQTWSDCQ8afqdyR4woUzhW",balanceA=2)
#
# address_from="ALcC96eesqb9pQTWSDCQ8afqdyR4woUzhW"
# multi_contract=createMultiSigContract(["0299dc85df93fee8ff2230af0418cf8c5000296f0aed514fcc0ab0dd969ce0bdb0","034e9d2751e1fec65a6a42bc097bdf55c7a79762df7d6e970277f46405c376683a"])
pass
# address_from=multi_contract["address"]
# verify_script=createVerifyScript("5221034e9d2751e1fec65a6a42bc097bdf55c7a79762df7d6e970277f46405c376683a2103eb0881d1d64754d50255bf16079ed6cbc3982463a8904cb919422b39178bef3f52ae")
# print ("verify script:",verify_script)
# time_stamp = TransactionAttribute(usage=TransactionAttributeUsage.Remark, data=bytearray.fromhex(hex(int(time.time()))[2:]))
# pre_txid= TransactionAttribute(usage=TransactionAttributeUsage.Remark1, data=bytearray.fromhex(hex_reverse("0xf95bc0f9682df5c74c35c64f9079c9498cc6f1004d72e016bb03c4e419578b8a")))
# outputTo= TransactionAttribute(usage=TransactionAttributeUsage.Remark2, data=bytearray.fromhex("d904f61978b83b706445d2c418e336de4d6261d2"))
# address_hash1=TransactionAttribute(usage=TransactionAttributeUsage.Script, data=ToAddresstHash("AZH8KcoZsgyzbYze6CMYsNdM1UJDQRxGdK").Data)
# address_hash2=TransactionAttribute(usage=TransactionAttributeUsage.Script, data=ToAddresstHash("AdoHFZV8fxnVQBZ881mdGhynjGC3156Skv").Data)
# txAttributes=[address_hash1,time_stamp,pre_txid,outputTo]
#
#
#
# op_data1= create_opdata(address_from="AZH8KcoZsgyzbYze6CMYsNdM1UJDQRxGdK",address_to="AbZNDqwCSZj4XJSGHmbQTSoHofE2PRMurT",value=1,contract_hash=TNC)
# op_data2= create_opdata(address_from="AdoHFZV8fxnVQBZ881mdGhynjGC3156Skv",address_to=address_from,value=1,contract_hash=TNC)
# print (op_data)
# tx=InvocationTransaction()
# tx.Version=1
# tx.Attributes=txAttributes
# tx.Script=binascii.unhexlify(op_data1)
#
# print(tx.get_tx_data())


# time_stamp = TransactionAttribute(usage=TransactionAttributeUsage.Remark, data=bytearray.fromhex(hex(int(time.time()))[2:]))
# address_hash=TransactionAttribute(usage=TransactionAttributeUsage.Script, data=ToAddresstHash("AJAd9ZaZCwLvdktHc1Rs7w3hmpVSBuTKzs").Data)
# outputTo= TransactionAttribute(usage=TransactionAttributeUsage.Remark2, data=ToAddresstHash("AJAd9ZaZCwLvdktHc1Rs7w3hmpVSBuTKzs").Data)
# txAttributes=[address_hash,time_stamp,outputTo]
#
#
#
# op_data= create_opdata(address_from="AJAd9ZaZCwLvdktHc1Rs7w3hmpVSBuTKzs",address_to="ALcC96eesqb9pQTWSDCQ8afqdyR4woUzhW",value=13,contract_hash=TNC)
# tx=InvocationTransaction()
# tx.Version=1
# tx.Attributes=txAttributes
# tx.Script=binascii.unhexlify(op_data)
#
# print(tx.get_tx_data())


# sadf=createRSMCContract(hashSelf="7880ddceb5101a29e05ea09da1ad310539dc8e69",hashOther="1a3db733023a855ac2077926c60e4c1fb4d5af00",pubkeyOther="03d8f667ff2068751e117cd6dbe3ebe286dbbc7fbb7b1ef0fbf5eb068e8b783a94",pubkeySelf="03ed45d1fdf6dbd5a6e5567b50d2b36b8ae5c1cd0123f26aba000fd3a72d6fbd28",magicTimestamp=time.time())
# print (sadf)