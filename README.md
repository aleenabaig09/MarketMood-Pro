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
- Produces a concise analyst summary

## Stocks Included

- Apple (`AAPL`)
- Microsoft (`MSFT`)
- Nvidia (`NVDA`)
- Amazon (`AMZN`)
- Meta (`META`)
- Tesla (`TSLA`)
- Alphabet / Google (`GOOGL`)

## Technologies Used

- Python
- Streamlit
- Pandas
- Plotly
- yFinance
- VADER Sentiment Analysis

## How to Run

Install dependencies:

```bash
pip install -r requirements.txt
```

Run the dashboard:

```bash
streamlit run app.py
```

## Notes

MarketMood Pro is an educational portfolio project. It is not investment advice and does not predict future stock performance.
