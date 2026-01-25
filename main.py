import json
from data_fetcher import (
    fetch_reit_data, 
    get_current_price, 
    fetch_fundamental_data,
    match_fundamental_data,
    get_sector_summary,
    get_sector_category
)
from analyzer import analyze_reit
from dashboard_gen import generate_dashboard
from telegram_bot import send_update
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def load_config():
    with open('reits_config.json', 'r') as f:
        return json.load(f)

def main():
    logger.info("Starting S-REITs Dashboard Update...")
    
    # Load configuration
    reits_config = load_config()
    logger.info(f"Loaded {len(reits_config)} REITs from config")
    
    # Fetch fundamental data from Fifth Person (single call)
    fundamental_data = fetch_fundamental_data()
    logger.info(f"Fetched fundamental data for {len(fundamental_data)} REITs")
    
    # Process each REIT
    all_reits_data = []
    
    for reit in reits_config:
        ticker = reit['ticker']
        name = reit['name']
        segment = reit['segment']
        
        logger.info(f"Processing {name} ({ticker})...")
        
        # Fetch historical data for technical analysis
        hist_data = fetch_reit_data(ticker)
        
        if hist_data is None or hist_data.empty:
            logger.warning(f"Skipping {name} - no historical data")
            continue
        
        # Get current price
        current_price = get_current_price(ticker)
        if current_price == 0:
            current_price = hist_data['Close'].iloc[-1]
        
        # Technical analysis
        analysis = analyze_reit(hist_data)
        
        # Match fundamental data
        fundamentals = match_fundamental_data(name, fundamental_data)
        
        # Build REIT data object
        reit_data = {
            'ticker': ticker,
            'name': name,
            'segment': segment,
            'sector': get_sector_category(segment),
            'price': round(current_price, 2),
            'change_pct': analysis['change_pct'],
            'rsi': analysis['rsi'],
            'trend': analysis['trend'],
            'insights': analysis['insights'],
            # Fundamental metrics (from Fifth Person)
            'dividend_yield': fundamentals['dividend_yield'] if fundamentals else None,
            'price_to_nav': fundamentals['price_to_nav'] if fundamentals else None,
            'nav': fundamentals['nav'] if fundamentals else None,
            'gearing_ratio': fundamentals['gearing_ratio'] if fundamentals else None,
            'dpu': fundamentals['dpu'] if fundamentals else None,
        }
        
        # Add fundamental insights
        if fundamentals:
            # Yield assessment
            if reit_data['dividend_yield'] and reit_data['dividend_yield'] > 7:
                reit_data['insights'].append(f"High yield ({reit_data['dividend_yield']}%)")
            
            # NAV assessment
            if reit_data['price_to_nav']:
                if reit_data['price_to_nav'] < 0.8:
                    reit_data['insights'].append(f"Deep discount to NAV ({reit_data['price_to_nav']}x)")
                elif reit_data['price_to_nav'] > 1.3:
                    reit_data['insights'].append(f"Premium to NAV ({reit_data['price_to_nav']}x)")
            
            # Gearing assessment
            if reit_data['gearing_ratio']:
                if reit_data['gearing_ratio'] > 45:
                    reit_data['insights'].append(f"High gearing ({reit_data['gearing_ratio']}%)")
                elif reit_data['gearing_ratio'] < 35:
                    reit_data['insights'].append(f"Conservative gearing ({reit_data['gearing_ratio']}%)")
        
        all_reits_data.append(reit_data)
        logger.info(f"  → Price: {reit_data['price']}, Yield: {reit_data['dividend_yield']}%, P/NAV: {reit_data['price_to_nav']}")
    
    if not all_reits_data:
        logger.error("No REIT data collected!")
        return
    
    # Calculate sector summary
    sector_summary = get_sector_summary(all_reits_data)
    logger.info(f"Sector summary: {sector_summary}")
    
    # Calculate portfolio-wide metrics
    yields = [r['dividend_yield'] for r in all_reits_data if r.get('dividend_yield')]
    pnavs = [r['price_to_nav'] for r in all_reits_data if r.get('price_to_nav')]
    gearings = [r['gearing_ratio'] for r in all_reits_data if r.get('gearing_ratio')]
    
    portfolio_metrics = {
        'avg_yield': round(sum(yields) / len(yields), 2) if yields else 0,
        'avg_pnav': round(sum(pnavs) / len(pnavs), 2) if pnavs else 0,
        'avg_gearing': round(sum(gearings) / len(gearings), 1) if gearings else 0,
    }
    
    logger.info(f"Portfolio metrics: {portfolio_metrics}")
    
    # Generate dashboard
    generate_dashboard(
        all_reits_data, 
        sector_summary=sector_summary,
        portfolio_metrics=portfolio_metrics
    )
    
    logger.info("Dashboard generation complete!")
    
    # Send Telegram update
    try:
        send_update(all_reits_data, portfolio_metrics=portfolio_metrics)
        logger.info("Telegram notification sent!")
    except Exception as e:
        logger.error(f"Failed to send Telegram update: {e}")
    
    return all_reits_data

if __name__ == "__main__":
    main()
