import pandas as pd
import numpy as np

def calculate_rsi(data, window=14):
    """Calculate RSI indicator."""
    delta = data['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()

    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

def calculate_sma(data, window=20):
    """Calculate Simple Moving Average."""
    return data['Close'].rolling(window=window).mean()

def analyze_reit(ticker, name, segment, df):
    """
    Analyzes the dataframe for a single REIT.
    Returns a dictionary of metrics and insights.
    """
    if df is None or df.empty:
        return None

    # Calculate indicators
    df['RSI'] = calculate_rsi(df)
    df['SMA_50'] = calculate_sma(df, window=50)
    df['SMA_20'] = calculate_sma(df, window=20)
    
    current_price = df['Close'].iloc[-1]
    prev_price = df['Close'].iloc[-2]
    price_change = ((current_price - prev_price) / prev_price) * 100
    
    rsi_val = df['RSI'].iloc[-1]
    sma_50_val = df['SMA_50'].iloc[-1]
    sma_20_val = df['SMA_20'].iloc[-1]
    
    # Trends
    trend = "Neutral"
    if current_price > sma_50_val:
        trend = "Bullish"
    elif current_price < sma_50_val:
        trend = "Bearish"
        
    # Opportunities & Risks
    insights = []
    status_color = "gray"
    
    if rsi_val < 30:
        insights.append("Oversold (RSI < 30) - Potential Buy Opportunity")
        status_color = "green"
    elif rsi_val > 70:
        insights.append("Overbought (RSI > 70) - Overvaluation Risk")
        status_color = "red"
        
    if current_price > sma_20_val and current_price > sma_50_val:
        insights.append("Strong Uptrend (Above 20 & 50 SMA)")
    elif current_price < sma_20_val and current_price < sma_50_val:
        insights.append("Downtrend (Below 20 & 50 SMA)")

    if not insights:
        insights.append("Trading within normal range")

    return {
        "ticker": ticker,
        "name": name,
        "segment": segment,
        "price": round(current_price, 3),
        "change_pct": round(price_change, 2),
        "rsi": round(rsi_val, 1),
        "trend": trend,
        "insights": insights,
        "status_color": status_color,
        "volume": int(df['Volume'].iloc[-1])
    }
