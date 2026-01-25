import yfinance as yf
import pandas as pd
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def fetch_reit_data(ticker, period="6mo"):
    """
    Fetches historical data for a given ticker.
    """
    try:
        logger.info(f"Fetching data for {ticker}...")
        stock = yf.Ticker(ticker)
        # Fetch history
        hist = stock.history(period=period)
        
        # Get info for current price (sometimes history is slightly delayed or we want more metadata)
        # stock.info is sometimes slow or unreliable, so we'll rely mostly on history for trends
        
        if hist.empty:
            logger.warning(f"No data found for {ticker}")
            return None
            
        return hist
    except Exception as e:
        logger.error(f"Error fetching data for {ticker}: {e}")
        return None

def get_current_price(ticker):
    try:
        stock = yf.Ticker(ticker)
        # Try fast info first
        return stock.fast_info.last_price
    except:
        # Fallback to history
        hist = stock.history(period="1d")
        if not hist.empty:
            return hist['Close'].iloc[-1]
        return 0.0
