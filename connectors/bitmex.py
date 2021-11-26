import hashlib
import hmac
import json
import logging
import threading
import time
import typing
from urllib.parse import urlencode

import requests
import websocket

logger = logging.getLogger()


class BitmexClient:
    """
    Initializes the BitmexClient. Make testnet parameter True to avoid using real live data,
    then include appropriate API keys
    """

    def __init__(self, public_key: str, secret_key: str, testnet: bool = False):
        if testnet:
            self._base_url = "https://testnet.bitmex.com/api/v1/"
            self._wss_url = "wss://testnet.bitmex.com/realtime"
        else:
            self._base_url = "https://www.bitmex.com/api/v1/"
            self._wss_url = "wss://www.bitmex.com/realtime"

        self._public_key = public_key
        self._secret_key = secret_key

        self.contracts = self.get_contracts()
        self.balances = self.get_balances()

        self.prices = dict()

        self._ws = None
        self._ws_id = 1

        thread = threading.Thread(target=self._start_ws)
        thread.start()

        logger.info("BitmexClient successfully initialized")

    def _generate_signature(self, data: typing.Dict) -> str:
        return hmac.new(self._secret_key.encode(), urlencode(data).encode(), hashlib.sha256).hexdigest()

    def _make_request(self, endpoint: str, data: typing.Dict = None, method: str = "GET") -> typing.Dict:
        if data is None:
            data = dict()
        data["timestamp"] = str(int(round(time.time() * 1000)))
        data["api-nonce"] = str(int(round(time.time() * 1000)))

        if method == "GET":
            response_object = requests.get(self._base_url + endpoint, params=data)
        elif method == "POST":
            response_object = requests.post(self._base_url + endpoint, data=data)
        else:
            raise ValueError("Invalid method")

        return response_object.json()

    def get_contracts(self):
        response_object = requests.get("https://testnet.bitmex.com/api/v1/instrument/active")
        print(response_object.status_code)

        contracts = []
        for contract in response_object.json():
            contracts.append(contract['symbol'])

        return contracts

    def get_historical_candles(self, symbol: str, interval: str, start: str, end: str):
        data = {
            "symbol": symbol,
            "binSize": interval,
            "count": 5000,
            "startTime": start,
            "endTime": end
        }

        response_object = requests.get(self._base_url + "trade/bucketed", params=data)

        return response_object.json()

    def get_balances(self):
        response_object = requests.get("https://testnet.bitmex.com/api/v1/user/margin")
        print(response_object.status_code)

        balances = []
        for balance in response_object.json():
            balances.append(balance['currency'])

        return balances

    def place_order(self, symbol: str, side: str, price: float, quantity: float):
        data = {
            "symbol": symbol,
            "side": side,
            "price": price,
            "orderQty": quantity,
            "ordType": "Limit"
        }

        response_object = requests.post(self._base_url + "order", data=data)
        print(response_object.status_code)

        return response_object.json()

    def cancel_order(self, order_id: str):
        data = {
            "orderID": order_id
        }

        response_object = requests.delete(self._base_url + "order", data=data)
        print(response_object.status_code)

        return response_object.json()

    def get_order_status(self, order_id: str):
        data = {
            "orderID": order_id
        }

        response_object = requests.get(self._base_url + "order", params=data)
        print(response_object.status_code)

        return response_object.json()

    def _start_ws(self):
        self._ws = websocket.WebSocketApp(self._wss_url,
                                          on_message=self._on_message,
                                          on_error=self._on_error,
                                          on_close=self._on_close)
        self._ws.run_forever()

    def _on_open(self):
        logger.info("BitmexClient websocket connection opened")

    def _on_close(self):
        logger.info("BitmexClient websocket connection closed")

    def _on_error(self, error):
        logger.error("BitmexClient websocket error: " + str(error))

    def _on_message(self, message):
        message = json.loads(message)
        if message["table"] == "orderBookL2":
            self._on_order_book_update(message)
        elif message["table"] == "trade":
            self._on_trade_update(message)
        elif message["table"] == "instrument":
            self._on_instrument_update(message)
        elif message["table"] == "margin":
            self._on_margin_update(message)
        else:
            logger.info("BitmexClient received unknown message: " + str(message))

    def _subscribe_channel(self, channel: str):
        self._ws.send(json.dumps({"op": "subscribe", "args": [channel]}))
