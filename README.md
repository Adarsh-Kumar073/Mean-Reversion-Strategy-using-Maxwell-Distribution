# **Maxwell Distribution-Based Trading Strategy**
This repository contains a Python implementation of a trading strategy that uses the Maxwell distribution to identify potential buy opportunities based on price deviations from a moving average. The strategy is further enhanced with stop-loss protection and dynamic position sizing.

# **📜 Strategy Overview**

**Concept:**
The Maxwell distribution is a statistical tool that models the distribution of values, particularly deviations from a central value (in this case, a moving average).
This strategy uses the cumulative distribution function (CDF) of the Maxwell distribution to identify when the price is undervalued relative to its moving average.

**Key Features:**

**Buy Signals:**
Triggered when the Maxwell CDF value is below a user-defined buy threshold (indicating price dips below a statistically significant level).

**Stop Loss:**
Automatically exits positions when the price drops below a defined percentage from the entry price.
Moving Average Filter:
Uses a simple moving average (SMA) to smooth price data.

**Position Sizing:**
Automatically calculates position size as a percentage of account equity for risk management.


# **⚙️ Functionality**
**Core Components:**

**Buy Signal Logic:**
Identifies dips in the price below the buy threshold of the Maxwell distribution's CDF.
**Stop Loss:**
Protects against large losses by automatically closing the position when the stop-loss condition is met.

**WebSocket Integration:**
Continuously listens to real-time price updates using WebSocket connections to make instant trading decisions.

**Excluded Features:**
Sell Signals: This implementation focuses exclusively on buy signals and exits via stop-loss.


# **🔧 Setup & Usage**
**Prerequisites:**
Python 3.8 or higher.

**Install dependencies:**
bash
Copy code
pip install requests socketio numpy
API Keys:
Replace the placeholders in the script with your trading platform's API key and secret:

python
Copy code
api_key = '<YOUR_API_KEY>'
api_secret = '<YOUR_API_SECRET>'
Running the Script:
Clone the repository:
bash
Copy code
git clone https://github.com/<your-username>/<your-repo-name>.git
cd <your-repo-name>
Run the trading bot:
bash
Copy code
python trading_bot.py

# **📊 Key Parameters**
Parameter	Description	Default Value
ma_period	Period for calculating the moving average.	44
scale_param	Scale parameter for the Maxwell distribution.	44
buy_threshold	Threshold for the Maxwell CDF to trigger buy signals.	0.1
stop_loss_pct	Stop loss percentage to minimize potential losses.	50%

# **📈 Strategy Workflow**
**Price Monitoring:**
The script listens to price updates via WebSocket in real-time.
**Signal Generation**:
Deviation from the moving average is calculated.
The Maxwell CDF is evaluated for buy signals.
**Position Management:**
Buys are placed when conditions are met.
Positions are closed if the stop-loss threshold is triggered.

# **🚀 Deployment**
**Options for Continuous Operation:
Run Locally:**
Use tools like tmux or screen to keep the bot running in the background.
**Deploy to a Server:**
Deploy on a cloud platform like AWS, GCP, or Azure for uninterrupted operation.
Alternatively, use Heroku or DigitalOcean for quick deployment.


# **Thresholds & Parameters:**
Modify ma_period, scale_param, and buy_threshold to fit your trading style.
**Risk Management:**
Adjust the stop-loss percentage (stop_loss_pct) to suit your risk appetite.
Asset Selection:
Update the subscribed symbols and parameters based on the market (e.g., BTCUSDT, ETHUSDT).

# **📌 Limitations**
**No Sell Signals:**
The current strategy focuses on buy opportunities and stop-loss exits.
**Real-Time Dependency:**
Requires continuous WebSocket connectivity for optimal performance.

# **⚠️ Disclaimer**
This strategy is for educational purposes only. Use at your own risk. The author is not responsible for any financial losses incurred while using this code. Always test thoroughly in a simulated environment before deploying in live trading.
