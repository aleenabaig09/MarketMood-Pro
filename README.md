# MarketMood Pro

MarketMood Pro is an interactive stock analytics dashboard that combines market performance, trading activity, volatility, headline sentiment, and earnings-event reactions.

## What It Does

- Pulls historical stock data using yFinance
- Tracks stock price, daily returns, and trading volume
- Calculates 20-day moving averages and rolling volatility
- Detects unusual trading-volume spikes
- Scores financial-news headlines as positive, neutral, or negative
- Compares headline sentiment with same-day stock returns
- Flags sentiment-price mismatches
- Generates a custom Market Reaction Score
- Analyzes stock performance around major earnings events

## Stocks Included

- Apple (`AAPL`)
- Microsoft (`MSFT`)
- Nvidia (`NVDA`)
- Amazon (`AMZN`)
- Meta (`META`)
- Tesla (`TSLA`)
- Alphabet / Google (`GOOGL`)

## Dashboard Tabs

### Overview
Shows price movement, moving averages, daily returns, trading volume, volatility, and unusual volume days.

### Sentiment Analysis
Scores saved financial-news headlines and compares sentiment with stock returns to identify possible market mismatches.

### Event Study
Shows cumulative stock returns around selected company events, such as earnings releases.

## Technologies Used

- Python
- Streamlit
- Pandas
- Plotly
- yFinance
- VADER Sentiment Analysis

## How to Run

Install the required packages:

```bash
pip install streamlit pandas yfinance plotly vaderSentiment