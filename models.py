class Balance:
    def __init__(self, info):
        self.initial_margin = float(info['initialMargin'])
        self.maintenance_margin = float(info['maintMargin'])
        self.margin_balance = float(info['marginBalance'])
        self.wallet_balance = float(info['walletBalance'])
        self.unrealized_pnl = float(info['unrealizedProfit'])


class Candle:
    def __init__(self, info):
        self.timestamp = float(info[0])
        self.open = float(info[1])
        self.high = float(info[2])
        self.low = float(info[3])
        self.close = float(info[4])
        self.volume = float(info[5])


class Contract:
    def __init__(self, info):
        self.symbol = info['symbol']
        self.base_asset = info['baseAsset']
        self.quote_asset = info['quoteAsset']
        self.price_precision = int(info['pricePrecision'])
        self.quantity_precision = int(info['quantityPrecision'])


class OrderStatus:
    def __init__(self, info):
        self.order_id = info['orderId']
        self.status = info['status']
        self.avg_price = float(info['avgPrice'])
