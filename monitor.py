from threading import Thread, Lock

import requests

lock = Lock()


class BaseMonitor(Thread):
    def __init__(self, currency: str, result: dict):
        super().__init__()
        self.name = None
        self.currency = currency
        self.result = result
        self.asks = None
        self.bids = None
        self.url = None
        self.params = {}

        self.__make_url()

    def run(self):
        resp = requests.get(self.url, params=self.params)
        data = None
        if resp.status_code == 200:
            data = self.__get_data(resp.json())

        lock.acquire()
        self.result[self.name] = data
        lock.release()

    def __make_url(self):
        raise NotImplementedError

    def __get_data(self, data):
        raise NotImplementedError


class BithumbMonitor(BaseMonitor):
    def __init__(self, currency: str, result: dict):
        super().__init__(currency, result)

    def run(self):
        pass

    def __make_url(self):
        self.currency = self.currency.upper()
        self.url = f"https://api.bithumb.com/public/orderbook/{self.currency}"

    def __get_data(self, data):
        asks = [(float(x['quantity']), int(x['price'])) for x in data['asks']]
        bids = [(float(x['quantity']), int(x['price'])) for x in data['bids']]
        return {"asks": asks, "bids": bids}


class KorbitMonitor(BaseMonitor):
    def __init__(self, currency: str, result: dict):
        super().__init__(currency, result)

    def run(self):
        pass

    def __make_url(self):
        self.currency = self.currency.lower()
        self.url = f"https://api.korbit.co.kr/v1/orderbook"
        self.params = {"currency_pair": f"{self.currency}_krw", "category": "all"}

    def __get_data(self, data):
        asks = [(float(x[1]), int(x[0])) for x in data["asks"]]
        bids = [(float(x[1]), int(x[0])) for x in data["bids"]]


