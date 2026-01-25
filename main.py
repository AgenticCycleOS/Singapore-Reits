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
from claude_analyzer import generate_full_analysis
from telegram_bot import send_update
import logging
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def load_config():
    with open('reits_config.json', 'r') as f:
        return json.load(f)

def main():
    logger.info("Starting S-REITs Dashboard Update...")
    
    reits_config = load_config()
    logger.info(f"Loaded {len(reits_config)} REITs from config")
    
    fundamental_data = fetch_fundamental_data()
    logger.info(f"Fetched fundamental data for {len(fundamental_data)} REITs")
    
    all_reits_data = []
    
    for reit in reits_config:
        ticker = reit['ticker']
        name = reit['name']
        segment = reit['segment']
        
        logger.info(f"Processing {name} ({ticker})...")
        
        hist_data = fetch_reit_data(ticker)
        
        if hist_data is None or hist_data.empty:
            logger.warning(f"Skipping {name} - no historical data")
            continue
        
        current_price = get_current_price(ticker)
        if current_price == 0:
            current_price = hist_data['Close'].iloc[-1]
        
        analysis = analyze_reit(hist_data)
        fundamentals = match_fundamental_data(name, fundamental_data)
        
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
        
        if fundamentals:
            if reit_data['dividend_yield'] and reit_data['dividend_yield'] > 7:
                reit_data['insights'].append(f"High yield ({reit_data['dividend_yield']}%)")
            if reit_data['price_to_nav']:
                if reit_data['price_to_nav'] < 0.8:
                    reit_data['insights'].append(f"Deep discount to NAV ({reit_data['price_to_nav']}x)")
                elif reit_data['price_to_nav'] > 1.3:
                    reit_data['insights'].append(f"Premium to NAV ({reit_data['price_to_nav']}x)")
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
    
    sector_summary = get_sector_summary(all_reits_data)
    
    yields = [r['dividend_yield'] for r in all_reits_data if r.get('dividend_yield')]
    pnavs = [r['price_to_nav'] for r in all_reits_data if r.get('price_to_nav')]
    gearings = [r['gearing_ratio'] for r in all_reits_data if r.get('gearing_ratio')]
    
    portfolio_metrics = {
        'avg_yield': round(sum(yields) / len(yields), 2) if yields else 0,
        'avg_pnav': round(sum(pnavs) / len(pnavs), 2) if pnavs else 0,
        'avg_gearing': round(sum(gearings) / len(gearings), 1) if gearings else 0,
    }
    
    # Generate AI analysis
    ai_analysis = None
    if os.environ.get('ANTHROPIC_API_KEY'):
        logger.info("Generating Claude AI analysis...")
        ai_analysis = generate_full_analysis(all_reits_data, portfolio_metrics, sector_summary)
        
        if ai_analysis.get('reit_analyses'):
            for reit in all_reits_data:
                if reit['ticker'] in ai_analysis['reit_analyses']:
                    reit['ai_analysis'] = ai_analysis['reit_analyses'][reit['ticker']]
    else:
        logger.info("ANTHROPIC_API_KEY not set - skipping AI analysis")
    
    generate_dashboard(
        all_reits_data, 
        sector_summary=sector_summary,
        portfolio_metrics=portfolio_metrics,
        ai_analysis=ai_analysis
    )
    
    if os.environ.get('TELEGRAM_BOT_TOKEN') and os.environ.get('TELEGRAM_CHAT_ID'):
        logger.info("Sending Telegram notification...")
        send_update(all_reits_data, portfolio_metrics, ai_analysis)
    
    logger.info("Dashboard generation complete!")
    return all_reits_data

if __name__ == "__main__":
    main()
