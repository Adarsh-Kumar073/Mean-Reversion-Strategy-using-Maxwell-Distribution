import json
import requests
import time
import hmac
import hashlib
import socketio
import collections
import urllib.parse
from scipy.stats import maxwell

# API keys
api_key = 'Enter your API KEY'
api_secret = 'Enter your API SECRET '

# WebSocket server URL
server_url = 'https://fawss.pi42.com/'
base_url = 'https://fapi.pi42.com/'

# Socket.IO client
sio = socketio.Client()

# Function to generate HMAC signature
def generate_signature(api_secret, data_to_sign):
    return hmac.new(api_secret.encode('utf-8'), data_to_sign.encode('utf-8'), hashlib.sha256).hexdigest()

# Function to place an order
def place_order(symbol, balance, close_price):
    timestamp = str(int(time.time() * 1000))
    balance = float(balance)
    close_price = float(close_price)
    quantity=(balance/close_price)*2.5
    params = {
        "timestamp": timestamp,  # Current timestamp in milliseconds
        "placeType": "ORDER_FORM",  # Type of order placement, e.g., 'ORDER_FORM'
        "quantity": quantity,  # Quantity of the asset to trade
        "side": "BUY",  # Order side, either 'BUY' or 'SELL'
        "symbol": f"{symbol}",  # Trading pair, e.g., Bitcoin to USDT
        "type": "MARKET",  # Order type, either 'MARKET' or 'LIMIT'
        'marginAsset': 'INR',
        "reduceOnly": False,  # Whether to reduce an existing position only
        "leverage": 5
    }
    data_to_sign = json.dumps(params, separators=(",", ":"))
    signature = generate_signature(api_secret, data_to_sign)
    headers = {
        "api-key": api_key,
        "signature": signature,
        "Content-Type": "application/json",
    }
    try:
        response = requests.post(f"{base_url}/v1/order/place-order", json=params, headers=headers)
        response.raise_for_status()
        response_data = response.json()
        print("Order placed successfully:", json.dumps(response_data, indent=4))
    except requests.exceptions.HTTPError as err:
        print(f"Error: {err.response.text if err.response else err}")
    except Exception as e:
        print(f"An unexpected error occurred: {str(e)}")



def close_all_positions():
    endpoint = "/v1/positions/close-all-positions"

    # Generate the current timestamp
    timestamp = str(int(time.time() * 1000))

    # Prepare the request payload
    params = {
        'timestamp': timestamp
    }

    # Convert the request body to a JSON string for signing
    data_to_sign = json.dumps(params, separators=(',', ':'))

    # Generate the signature (ensure `generate_signature` is properly defined)
    signature = generate_signature(api_secret, data_to_sign)

    # Headers for the DELETE request
    headers = {
        'api-key': api_key,
        'Content-Type': 'application/json',
        'signature': signature
    }

    # Construct the full URL
    cancel_orders_url = f"{base_url}{endpoint}"

    try:
        # Send the DELETE request to cancel all orders
        response = requests.delete(cancel_orders_url, json=params, headers=headers)
        response.raise_for_status()  # Raises an error for 4xx/5xx responses
        response_data = response.json()
        print('All orders canceled successfully:', json.dumps(response_data, indent=4))
    except requests.exceptions.HTTPError as err:
        print(f"Failed {response.status_code}: {response.text}")
    except Exception as e:
        print(f"An unexpected error occurred: {str(e)}")

def get_futures_wallet_details():
    endpoint = "/v1/wallet/futures-wallet/details"

    # Generate the current timestamp
    timestamp = str(int(time.time() * 1000))

    # Optional parameters with timestamp
    params = {
        'timestamp': timestamp
    }
    data_to_sign = urllib.parse.urlencode(params)  # Convert to query string


    # Generate the signature (ensure `generate_signature` is properly defined)
    signature = generate_signature(api_secret, data_to_sign)

    # Headers for the GET request
    headers = {
        'api-key': api_key,
        'Content-Type': 'application/json',
        'signature': signature
    }
    # Construct the full URL
    wallet_details_url = f"{base_url}{endpoint}"

    try:
        # Send the GET request to fetch the futures wallet details
        response = requests.get(wallet_details_url, headers=headers, params=params)
        response.raise_for_status()  # Raises an error for 4xx/5xx responses
        response_data = response.json()
        inr_balance = response_data.get("inrBalance")
        return inr_balance
    except requests.exceptions.HTTPError as err:
        print(f"Failed {response.status_code}: {response.text}")
    except Exception as e:
        print(f"An unexpected error occurred: {str(e)}")


# Variables for strategy parameters
MA_PERIOD = 44
SCALE_PARAM = 44
BUY_THRESHOLD = 0.1
SELL_THRESHOLD = 0.9
STOP_LOSS_PCT = 50
COOLDOWN_PERIOD = 60
state = {"trade": 0}

# Candle data storage and cooldown tracking
candle_data = {'ETHUSDT': collections.deque(maxlen=MA_PERIOD)}
last_sell_bar = {symbol: None for symbol in candle_data}

@sio.event
def connect():
    print('Connected to WebSocket server')
    subscribe_to_topics()

@sio.event
def disconnect():
    print('Disconnected from WebSocket server')

@sio.event
def connect_error(data):
    print('Socket.IO connection error:', data)

def subscribe_to_topics():
    topics = ['ethusdt@kline_2h']
    sio.emit('subscribe', {'params': topics})

    @sio.on('kline')
    def on_kline(data):
        symbol = data['ps']
        close_price = float(data['k']['c'])

        # Update candle data
        if symbol in candle_data:
            candle_data[symbol].append(close_price)

            if len(candle_data[symbol]) == MA_PERIOD:
                # Calculate moving average and deviation
                moving_average = sum(candle_data[symbol]) / MA_PERIOD
                deviation = close_price - moving_average

                # Maxwell distribution CDF
                cdf = 1 - (2.71828 ** -((deviation / SCALE_PARAM) ** 2))

                # Determine buy signal
                buy_signal = (cdf < BUY_THRESHOLD and state["trade"] ==0)

                # Determine sell signal
                close_signal = (
                    cdf > SELL_THRESHOLD
                    and (last_sell_bar[symbol] is None or time.time() - last_sell_bar[symbol] > COOLDOWN_PERIOD)
                )

                # Check stop loss
                stop_loss = moving_average * (1 - STOP_LOSS_PCT / 100)

                print(f"{symbol} | Price: {close_price}, MA: {moving_average}, Deviation: {deviation}, CDF: {cdf:.4f}")

                if buy_signal:
                    balance= get_futures_wallet_details()
                    print(f"{symbol}: Buy signal detected (CDF: {cdf:.4f})")
                    place_order(symbol, balance,close_price)
                    state["trade"]=1


                if close_signal:
                    print(f"{symbol}: Close signal detected (CDF: {cdf:.4f})")
                    close_all_positions()
                    last_sell_bar[symbol] = time.time()
                    state["trade"]= 0


                # Stop loss check
                if close_price <= stop_loss:
                    print(f"{symbol}: Stop loss triggered at {close_price}")
                    close_all_positions()
                    state["trade"]= 0

            else:
                print(f"Gathering data for {symbol}... ({len(candle_data[symbol])}/{MA_PERIOD})")

if __name__ == "__main__":
    try:
        sio.connect(server_url)
        print("WebSocket connection established. Listening for updates...")
        sio.wait()
    except Exception as e:
        print(f"An error occurred: {e}")
