import logging

logger = logging.getLogger(__name__)

class RPCException(Exception):
    pass

class RPC(object):
    def __init__(self, address, username, password):
        self.address = address
        self.username = username
        self.password = password

    def make_call(self, method, params=[]):
        import requests, json
        url = "http://{username}:{password}@{address}/".format(
            username=self.username, 
            password=self.password, 
            address=self.address
        )
        headers = {
            'content-type': 'application/json'
        }
        data = {
            "method": method,
            "params": params,
            "jsonrpc": "1.0"
        }
        response = requests.post(url, data=json.dumps(data), headers=headers)
        response = response.json()
        if response['error'] == None:
            return response['result']
        else:
            logging.error('RPC returned error: %s' % str(response))
            raise RPCException(response['error'])
