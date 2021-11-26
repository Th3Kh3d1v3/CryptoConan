import logging
import tkinter as tk

from config import *
from connectors.binance_futures import BinanceFuturesClient
from connectors.bitmex import BitmexClient

logger = logging.getLogger()

logger.setLevel(logging.INFO)

stream_handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s %(levelname)s :: %(message)s')
stream_handler.setFormatter(formatter)
stream_handler.setLevel(logging.INFO)

file_handler = logging.FileHandler('info.log')
file_handler.setFormatter(formatter)
file_handler.setLevel(logging.DEBUG)

logger.addHandler(stream_handler)
logger.addHandler(file_handler)

if __name__ == '__main__':
    if Binance:
        binance = BinanceFuturesClient(BINANCE_API_KEY, BINANCE_SECRET_KEY, True)

    if Bitmex:
        bitmex = BitmexClient(BITMEX_API_KEY, BITMEX_SECRET_KEY, True)

    root = tk.Tk()
    root.mainloop()
