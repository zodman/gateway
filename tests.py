import requests
import unittest

class TestNet(unittest.TestCase):
    # run gw on testnet_mode

    url = "http://localhost:8888/rest/v1/"
    address = "mo6Qh6iEhzHnt1R8jRQwagaBeXFv5eX2W4"

    def test_testnet(self):
        net = requests.get(self.url + "net/").json()
        self.assertTrue(net.get("chain") == "testnet")

    def test_address(self):
        res = requests.get(self.url + "address/%s" % self.address).json()
        self.assertTrue(res.get("status") == "success")
        self.assertTrue("address" in res["data"])




if __name__  == '__main__':
    unittest.main()
