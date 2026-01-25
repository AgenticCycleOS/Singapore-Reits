import json
import logging
from data_fetcher import fetch_reit_data
from analyzer import analyze_reit
from dashboard_gen import generate_dashboard
from telegram_bot import send_telegram_summary

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def load_config(path="reits_config.json"):
    with open(path, "r") as f:
        return json.load(f)

def main():
    logger.info("Starting S-REITs Dashboard Update...")
    
    # 1. Load Config
    try:
        reits = load_config()
    except Exception as e:
        logger.error(f"Failed to load config: {e}")
        return

    results = []
    
    # 2. Process each REIT
    for reit in reits:
        ticker = reit['ticker']
        name = reit['name']
        segment = reit['segment']
        
        # Fetch Data
        df = fetch_reit_data(ticker)
        
        # Analyze
        analysis = analyze_reit(ticker, name, segment, df)
        
        if analysis:
            results.append(analysis)
            logger.info(f"Analyzed {ticker}: {analysis['change_pct']}%")
            
    if not results:
        logger.error("No results to generate dashboard.")
        return

    # 3. Generate Dashboard
    generate_dashboard(results)
    
    # 4. Notify via Telegram
    send_telegram_summary(results)
    
    logger.info("Update Complete.")

if __name__ == "__main__":
    main()
