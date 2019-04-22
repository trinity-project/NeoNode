import requests


class NeoCliRpc(object):

    def __init__(self,rpc_uri):
        self.rpc_uri = rpc_uri


    def bulid_request_body(self,method,parameters):
        data = {
            "jsonrpc": "2.0",
            "method": method,
            "params": parameters,
            "id": 1
        }
        return data

    def make_request(self,data):
        res = requests.post(self.rpc_uri, json=data).json()
        return res.get("result",None)


    def get_block(self,block_height):
        data = self.bulid_request_body("getblock",[block_height,1])
        return self.make_request(data)


    def get_application_log(self,tx_id):
        data = self.bulid_request_body("getapplicationlog",[tx_id])
        return self.make_request(data)


    def get_transaction_height(self,tx_id):
        data = self.bulid_request_body("gettransactionheight",[tx_id])
        return self.make_request(data)

    def get_token_info(self,token_address):
        token_info = []
        for attr in ["name", "symbol", "decimals"]:
            data = self.bulid_request_body("invokefunction",[token_address,attr,[]] )
            res = self.make_request(data)
            value = res.get("stack")[0].get("value")
            if res.get("stack")[0].get("type") == "ByteArray":
                value = bytearray.fromhex(value).decode()

            token_info.append(value)

        return token_info
