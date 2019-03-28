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
        self.make_request(data)


    def get_application_log(self,tx_id):
        data = self.bulid_request_body("getapplicationlog",[tx_id])
        self.make_request(data)