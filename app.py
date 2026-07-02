import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.express as px
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

# -----------------------------
# PAGE SETUP
# -----------------------------
st.set_page_config(
    page_title="MarketMood Pro",
    page_icon="📈",
    layout="wide"
)

st.markdown("""
<style>
    .main {
        padding-top: 1rem;
    }

    [data-testid="stMetricValue"] {
        font-size: 26px;
    }

    [data-testid="stMetricLabel"] {
        font-size: 14px;
    }
</style>
""", unsafe_allow_html=True)

# -----------------------------
# TITLE
# -----------------------------
st.title("MarketMood Pro")
st.caption(
    "Stock sentiment, volatility, volume, and event-reaction analytics dashboard "
    "— educational use only, not investment advice."
)

# -----------------------------
# SIDEBAR
# -----------------------------
st.sidebar.title("MarketMood Controls")

ticker = st.sidebar.selectbox(
    "Choose a stock",
    ["AAPL", "MSFT", "NVDA", "AMZN", "META", "TSLA", "GOOGL"]
)

time_period = st.sidebar.selectbox(
    "Choose time period",
    ["6mo", "1y", "2y", "5y"],
    index=2
)

st.sidebar.markdown("---")
st.sidebar.caption(
    "Analyzes stock prices, volume, volatility, headline sentiment, "
    "and earnings-event reactions."
)

# -----------------------------
# STOCK DATA
# -----------------------------
@st.cache_data
def load_stock_data(stock_ticker, period):
    data = yf.download(
        stock_ticker,
        period=period,
        auto_adjust=False
    )

    if isinstance(data.columns, pd.MultiIndex):
        data.columns = data.columns.get_level_values(0)

    data = data.reset_index()

    data["Daily Return"] = data["Close"].pct_change() * 100
    data["20 Day Moving Average"] = data["Close"].rolling(20).mean()
    data["20 Day Volatility"] = data["Daily Return"].rolling(20).std()

    data["Average Volume"] = data["Volume"].rolling(20).mean()
    data["Volume Std"] = data["Volume"].rolling(20).std()

    data["Volume Z-Score"] = (
        (data["Volume"] - data["Average Volume"])
        / data["Volume Std"]
    )

    data["Volume Spike"] = data["Volume Z-Score"] > 2
    data["Date Only"] = pd.to_datetime(data["Date"]).dt.date

    return data


stock_data = load_stock_data(ticker, time_period)

if stock_data.empty:
    st.error("No stock data was found. Try another stock or time period.")
    st.stop()

latest_price = stock_data["Close"].iloc[-1]
previous_price = stock_data["Close"].iloc[-2]

daily_change = (
    (latest_price - previous_price)
    / previous_price
) * 100

latest_ma = stock_data["20 Day Moving Average"].iloc[-1]
latest_volatility = stock_data["20 Day Volatility"].iloc[-1]

# -----------------------------
# HEADLINES + SENTIMENT
# -----------------------------
@st.cache_data
def load_headlines():
    headlines_data = pd.read_csv("data/headlines.csv")
    headlines_data["date"] = pd.to_datetime(headlines_data["date"])

    analyzer = SentimentIntensityAnalyzer()

    headlines_data["Sentiment Score"] = headlines_data["headline"].apply(
        lambda headline: analyzer.polarity_scores(str(headline))["compound"]
    )

    def sentiment_label(score):
        if score >= 0.3:
            return "Positive"
        elif score <= -0.3:
            return "Negative"
        return "Neutral"

    headlines_data["Sentiment"] = headlines_data["Sentiment Score"].apply(
        sentiment_label
    )

    return headlines_data


headlines = load_headlines()

selected_headlines = headlines[
    (headlines["ticker"] == ticker)
    & (headlines["date"] >= pd.to_datetime(stock_data["Date"].min()))
    & (headlines["date"] <= pd.to_datetime(stock_data["Date"].max()))
].copy()

# -----------------------------
# MERGE SENTIMENT + STOCK DATA
# -----------------------------
if not selected_headlines.empty:
    selected_headlines["date_only"] = selected_headlines["date"].dt.date

    daily_sentiment = (
        selected_headlines
        .groupby("date_only", as_index=False)["Sentiment Score"]
        .mean()
    )

    sentiment_return = stock_data.merge(
        daily_sentiment,
        left_on="Date Only",
        right_on="date_only",
        how="inner"
    )
else:
    sentiment_return = pd.DataFrame()

# -----------------------------
# REACTION LABELS + SCORE
# -----------------------------
def reaction_label(row):
    sentiment = row["Sentiment Score"]
    stock_return = row["Daily Return"]

    if sentiment >= 0.3 and stock_return > 0:
        return "Matched Positive Reaction"

    elif sentiment >= 0.3 and stock_return < 0:
        return "Sentiment-Price Mismatch"

    elif sentiment <= -0.3 and stock_return < 0:
        return "Matched Negative Reaction"

    elif sentiment <= -0.3 and stock_return > 0:
        return "Negative News, Stock Resilient"

    elif abs(sentiment) < 0.3 and abs(stock_return) > 2:
        return "Large Move With Neutral News"

    return "Mixed / Neutral Reaction"


def calculate_reaction_score(row):
    sentiment = row["Sentiment Score"]
    stock_return = row["Daily Return"]

    score = 50
    score += sentiment * 25
    score += stock_return * 8

    if sentiment >= 0.3 and stock_return > 0:
        score += 15

    elif sentiment >= 0.3 and stock_return < 0:
        score -= 15

    elif sentiment <= -0.3 and stock_return < 0:
        score -= 15

    elif sentiment <= -0.3 and stock_return > 0:
        score += 15

    return max(0, min(100, round(score, 1)))


def score_label(score):
    if score >= 75:
        return "Strong Positive Reaction"
    elif score >= 60:
        return "Positive Reaction"
    elif score >= 40:
        return "Mixed Reaction"
    elif score >= 25:
        return "Negative Reaction"
    return "Strong Negative Reaction"


if not sentiment_return.empty:
    sentiment_return["Reaction Label"] = sentiment_return.apply(
        reaction_label,
        axis=1
    )

    sentiment_return["Market Reaction Score"] = sentiment_return.apply(
        calculate_reaction_score,
        axis=1
    )

    sentiment_return["Reaction Score Label"] = sentiment_return[
        "Market Reaction Score"
    ].apply(score_label)

# -----------------------------
# TABS
# -----------------------------
overview_tab, sentiment_tab, event_tab, summary_tab = st.tabs([
    "📊 Overview",
    "🧠 Sentiment Analysis",
    "📅 Event Study",
    "📋 Analyst Summary"
])

# =================================================
# OVERVIEW TAB
# =================================================
with overview_tab:
    st.subheader(f"{ticker} Market Overview")

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Current Price", f"${latest_price:.2f}")
    col2.metric("Daily Change", f"{daily_change:.2f}%")
    col3.metric("20-Day Average", f"${latest_ma:.2f}")
    col4.metric("20-Day Volatility", f"{latest_volatility:.2f}%")

    st.markdown("---")

    fig_price = px.line(
        stock_data,
        x="Date",
        y="Close",
        title=f"{ticker} Stock Price vs 20-Day Moving Average"
    )

    fig_price.add_scatter(
        x=stock_data["Date"],
        y=stock_data["20 Day Moving Average"],
        mode="lines",
        name="20-Day Moving Average"
    )

    st.plotly_chart(fig_price, use_container_width=True)

    left_chart, right_chart = st.columns(2)

    with left_chart:
        fig_returns = px.bar(
            stock_data,
            x="Date",
            y="Daily Return",
            title=f"{ticker} Daily Return (%)"
        )

        st.plotly_chart(fig_returns, use_container_width=True)

    with right_chart:
        fig_volume = px.bar(
            stock_data,
            x="Date",
            y="Volume",
            title=f"{ticker} Trading Volume"
        )

        st.plotly_chart(fig_volume, use_container_width=True)

    st.subheader("Rolling Volatility")

    fig_volatility = px.line(
        stock_data,
        x="Date",
        y="20 Day Volatility",
        title=f"{ticker} 20-Day Rolling Volatility"
    )

    st.plotly_chart(fig_volatility, use_container_width=True)

    st.subheader("Unusual Trading Volume Days")

    volume_spikes = stock_data[stock_data["Volume Spike"]]

    if volume_spikes.empty:
        st.info("No unusual volume spikes were found in this period.")
    else:
        st.dataframe(
            volume_spikes[
                ["Date", "Close", "Volume", "Volume Z-Score"]
            ],
            use_container_width=True
        )

# =================================================
# SENTIMENT TAB
# =================================================
with sentiment_tab:
    st.subheader(f"{ticker} News Sentiment Analysis")

    if selected_headlines.empty:
        st.info(
            "No headline data is available for this stock during the selected "
            "time period. Choose 2y or 5y to see the saved headline data."
        )
    else:
        st.dataframe(
            selected_headlines[
                ["date", "headline", "Sentiment Score", "Sentiment"]
            ],
            use_container_width=True
        )

    st.markdown("---")

    st.subheader("Sentiment vs Stock Return")

    if sentiment_return.empty:
        st.info(
            "No matching headline dates were found for this stock and time period."
        )
    else:
        fig_sentiment_return = px.scatter(
            sentiment_return,
            x="Sentiment Score",
            y="Daily Return",
            size="Volume",
            hover_data=[
                "Date",
                "Close",
                "Reaction Label",
                "Market Reaction Score"
            ],
            title=f"{ticker}: Headline Sentiment vs Daily Stock Return"
        )

        st.plotly_chart(fig_sentiment_return, use_container_width=True)

        st.subheader("Market Reaction Labels")

        st.dataframe(
            sentiment_return[
                [
                    "Date",
                    "Close",
                    "Daily Return",
                    "Sentiment Score",
                    "Reaction Label",
                    "Market Reaction Score",
                    "Reaction Score Label"
                ]
            ],
            use_container_width=True
        )

        st.subheader("Top Insight")

        strongest_reaction = sentiment_return.loc[
            sentiment_return["Market Reaction Score"].idxmax()
        ]

        mismatch_days = sentiment_return[
            sentiment_return["Reaction Label"]
            == "Sentiment-Price Mismatch"
        ]

        if not mismatch_days.empty:
            mismatch_day = mismatch_days.iloc[0]

            st.warning(
                f"""
                **Sentiment-Price Mismatch Detected**

                On {mismatch_day["Date"].strftime("%B %d, %Y")},
                {ticker} had a positive sentiment score of
                {mismatch_day["Sentiment Score"]:.2f}, but the stock returned
                {mismatch_day["Daily Return"]:.2f}% that day.
                """
            )

        st.success(
            f"""
            **Strongest Market Reaction**

            On {strongest_reaction["Date"].strftime("%B %d, %Y")},
            {ticker} received a Market Reaction Score of
            {strongest_reaction["Market Reaction Score"]:.1f}/100.

            Reaction type: **{strongest_reaction["Reaction Score Label"]}**
            """
        )

# =================================================
# EVENT STUDY TAB
# =================================================
with event_tab:
    st.subheader("Earnings Event Study")

    events = pd.read_csv("data/events.csv")
    events["event_date"] = pd.to_datetime(events["event_date"])

    selected_events = events[events["ticker"] == ticker]

    if selected_events.empty:
        st.info("No saved events are available for this stock yet.")
    else:
        selected_event = st.selectbox(
            "Choose an event",
            selected_events["event_description"]
        )

        event_row = selected_events[
            selected_events["event_description"] == selected_event
        ].iloc[0]

        event_date = event_row["event_date"]

        event_window = stock_data[
            (stock_data["Date"] >= event_date - pd.Timedelta(days=5))
            & (stock_data["Date"] <= event_date + pd.Timedelta(days=5))
        ].copy()

        if event_window.empty:
            st.warning(
                "This event is outside your selected stock-data period. "
                "Choose 2y or 5y in the sidebar."
            )
        else:
            event_window["Cumulative Return"] = (
                event_window["Close"]
                / event_window["Close"].iloc[0]
                - 1
            ) * 100

            fig_event = px.line(
                event_window,
                x="Date",
                y="Cumulative Return",
                title=f"{ticker} Price Reaction Around: {selected_event}"
            )

            st.plotly_chart(fig_event, use_container_width=True)

            st.dataframe(
                event_window[
                    [
                        "Date",
                        "Close",
                        "Daily Return",
                        "Volume",
                        "Cumulative Return"
                    ]
                ],
                use_container_width=True
            )