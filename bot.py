import websocket
import json
import pprint
import talib
import numpy
import config
from binance.client import Client
from binance.enums import *

# This is where our bot will obtain the data from
SOCKET = "wss://testnet.binance.vision/ws/ethusdt@kline_1m"

RSI_PERIOD = 14
# When everyone is buying the crypto, price is high
RSI_OVERBOUGHT = 70
# When everyone is seleing the crypto, price is low
RSI_OVERSOLD = 30
TRADE_SYMBOL = 'ETHUSD'
TRADE_QUANTITY = 0.05

closes = []
in_position = False

# Binance api key, obtained from the binance website
api_key = 'vk8bUCtlI50nMU3fyNhPTHOlFoY07lcTMXkWfjLUwyK2dV7KTTacOkQcHRzMOlOr'
# Binance secret api key, obtained from the binance website
api_secret = 'API KEYS'

# basically connects the bot to your account
client = Client(config.api_key, config.api_secret, tld='lv')


def order(side, quantity, symbol, order_type=ORDER_TYPE_MARKET):
    try:
        print("sending order")
        # sends and order to purchase an amount of the crypto
        order = client.create_order(
            symbol=symbol, side=side, type=order_type, quantity=quantity)
        print(order)
    except Exception as e:
        # if things did not go to plan this message will pop up
        print(f"an exception occured - {e}")
        return False

    return True

# opens the connection to binance


def on_open(ws):
    print('opened connection')

# closes the connection to binance


def on_close(ws):
    print('closed connection')


def on_message(ws, message):
    global closes, in_position
    print('received message')
    # this is a json dictionary with all of data
    json_message = json.loads(message)
    pprint.pprint(json_message)

    # json dict within the json dict
    candle = json_message['k']

    # this is a part of the candle json dict and tells you when there is a difference in the market
    is_candle_closed = candle['x']
    close = candle['c']

    # just notifies you when the process is closed
    if is_candle_closed:
        print(f"candle closed at {close}")
        closes.append(float(close))
        print("closes")
        print(closes)

        if len(closes) > RSI_PERIOD:
            np_closes = numpy.array(closes)
            rsi = talib.RSI(np_closes, RSI_PERIOD)
            print("all rsis calculated so far")
            print(rsi)
            last_rsi = rsi[-1]
            print(f"the current rsi is {last_rsi}")

            if last_rsi > RSI_OVERBOUGHT:
                if in_position:
                    print("Overbought! Sell! Sell! Sell!")
                    # put binance sell logic here
                    order_succeeded = order(
                        SIDE_SELL, TRADE_QUANTITY, TRADE_SYMBOL)
                    if order_succeeded:
                        in_position = False
                else:
                    print("It is overbought, but we don't own any. Nothing to do.")

            if last_rsi < RSI_OVERSOLD:
                if in_position:
                    print("It is oversold, but you already own it, nothing to do.")
                else:
                    print("Oversold! Buy! Buy! Buy!")
                    # put binance buy order logic here
                    order_succeeded = order(
                        SIDE_BUY, TRADE_QUANTITY, TRADE_SYMBOL)
                    if order_succeeded:
                        in_position = True


ws = websocket.WebSocketApp(SOCKET, on_open=on_open,
                            on_close=on_close, on_message=on_message)
ws.run_forever()
