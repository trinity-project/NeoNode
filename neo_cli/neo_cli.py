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



    def get_token_info(tokenAddress):

        data = {
            "jsonrpc": "2.0",
            "method": "invokefunction",
            "id": 3
        }

        token_info = []

        try:
            for attr in ["name", "symbol", "decimals"]:
                data["params"] = [tokenAddress, attr, []]
                res = requests.post(random.choice(setting.NEO_RPC_APPLICATION_LOG), json=data).json()
                value = res.get("result").get("stack")[0].get("value")
                if res.get("result").get("stack")[0].get("type") == "ByteArray":
                    value = bytearray.fromhex(value).decode()
                token_info.append(value)

            return token_info
        except Exception as e:
            logger.error(e)
            return None

