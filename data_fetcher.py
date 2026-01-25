import yfinance as yf
import pandas as pd
import requests
from bs4 import BeautifulSoup
import logging
import re

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Fifth Person S-REIT data URL
FIFTH_PERSON_URL = "https://sreit.fifthperson.com/"

def fetch_fundamental_data():
    """
    Scrapes fundamental REIT data from Fifth Person website.
    Returns a dict keyed by REIT name with yield, P/NAV, gearing, etc.
    Falls back to cached data if scraping fails.
    """
    try:
        logger.info("Fetching fundamental data from Fifth Person...")
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        response = requests.get(FIFTH_PERSON_URL, headers=headers, timeout=30)
        response.raise_for_status()
        
        # Parse HTML tables with pandas
        tables = pd.read_html(response.text)
        
        if not tables:
            logger.warning("No tables found on Fifth Person page")
            return get_fallback_fundamental_data()
        
        # First table contains REIT data
        df = tables[0]
        logger.info(f"Found {len(df)} REITs in fundamental data")
        
        # Build lookup dict by name (normalized)
        fundamental_data = {}
        for _, row in df.iterrows():
            try:
                name = str(row.get('Name', '')).strip()
                if not name or name == 'nan':
                    continue
                    
                # Normalize name for matching
                name_key = normalize_reit_name(name)
                
                fundamental_data[name_key] = {
                    'full_name': name,
                    'dividend_yield': safe_float(row.get('Distribution Yield', '0').replace('%', '')),
                    'price_to_nav': safe_float(row.get('Price to Book', 0)),
                    'nav': safe_float(row.get('NAV', 0)),
                    'dpu': safe_float(row.get('DPU', 0)),
                    'gearing_ratio': safe_float(str(row.get('Gearing Ratio*', '0')).replace('%', '')),
                    'property_yield': safe_float(str(row.get('Property Yield', '0')).replace('%', '')),
                }
            except Exception as e:
                logger.warning(f"Error parsing row: {e}")
                continue
        
        if not fundamental_data:
            logger.warning("No data parsed, using fallback")
            return get_fallback_fundamental_data()
            
        logger.info(f"Parsed fundamental data for {len(fundamental_data)} REITs")
        return fundamental_data
        
    except Exception as e:
        logger.error(f"Error fetching fundamental data: {e}")
        logger.info("Using fallback fundamental data")
        return get_fallback_fundamental_data()


def get_fallback_fundamental_data():
    """
    Returns cached fundamental data as fallback when scraping fails.
    Data from Fifth Person as of Jan 2026.
    """
    return {
        'capitaland integrated commercial': {
            'full_name': 'CapitaLand Integrated Commercial Trust',
            'dividend_yield': 4.59,
            'price_to_nav': 1.12,
            'nav': 2.12,
            'dpu': 0.1088,
            'gearing_ratio': 38.5,
            'property_yield': 4.65,
        },
        'capitaland ascendas': {
            'full_name': 'CapitaLand Ascendas REIT',
            'dividend_yield': 5.26,
            'price_to_nav': 1.27,
            'nav': 2.27,
            'dpu': 0.1521,
            'gearing_ratio': 37.7,
            'property_yield': 6.10,
        },
        'mapletree logistics': {
            'full_name': 'Mapletree Logistics Trust',
            'dividend_yield': 5.53,
            'price_to_nav': 1.04,
            'nav': 1.31,
            'dpu': 0.0752,
            'gearing_ratio': 44.4,
            'property_yield': 4.70,
        },
        'mapletree industrial': {
            'full_name': 'Mapletree Industrial Trust',
            'dividend_yield': 6.43,
            'price_to_nav': 1.23,
            'nav': 1.71,
            'dpu': 0.1357,
            'gearing_ratio': 40.6,
            'property_yield': 6.53,
        },
        'mapletree pan asia commercial': {
            'full_name': 'Mapletree Pan Asia Commercial Trust',
            'dividend_yield': 5.42,
            'price_to_nav': 0.83,
            'nav': 1.78,
            'dpu': 0.0802,
            'gearing_ratio': 38.8,
            'property_yield': 4.37,
        },
        'frasers logistics commercial': {
            'full_name': 'Frasers Logistics & Commercial Trust',
            'dividend_yield': 5.78,
            'price_to_nav': 0.94,
            'nav': 1.10,
            'dpu': 0.0595,
            'gearing_ratio': 35.7,
            'property_yield': 4.86,
        },
        'frasers centrepoint': {
            'full_name': 'Frasers Centrepoint Trust',
            'dividend_yield': 5.34,
            'price_to_nav': 1.02,
            'nav': 2.23,
            'dpu': 0.1211,
            'gearing_ratio': 39.6,
            'property_yield': 4.55,
        },
        'keppel dc': {
            'full_name': 'Keppel DC REIT',
            'dividend_yield': 4.28,
            'price_to_nav': 1.44,
            'nav': 1.53,
            'dpu': 0.0945,
            'gearing_ratio': 31.5,
            'property_yield': 5.31,
        },
        'suntec': {
            'full_name': 'Suntec REIT',
            'dividend_yield': 4.36,
            'price_to_nav': 0.69,
            'nav': 2.046,
            'dpu': 0.0619,
            'gearing_ratio': 42.4,
            'property_yield': 3.67,
        },
        'parkway life': {
            'full_name': 'Parkway Life REIT',
            'dividend_yield': 3.60,
            'price_to_nav': 1.72,
            'nav': 2.41,
            'dpu': 0.1492,
            'gearing_ratio': 34.8,
            'property_yield': 5.54,
        },
    }


def normalize_reit_name(name):
    """Normalize REIT name for matching between data sources."""
    name = name.lower()
    # Remove common suffixes
    name = re.sub(r'\s*(reit|trust)$', '', name)
    # Remove special characters
    name = re.sub(r'[^\w\s]', '', name)
    # Normalize whitespace
    name = ' '.join(name.split())
    return name


def safe_float(value, default=0.0):
    """Safely convert value to float."""
    try:
        if pd.isna(value) or value == '' or value == 'nan':
            return default
        return float(value)
    except (ValueError, TypeError):
        return default


def match_fundamental_data(reit_name, fundamental_data):
    """
    Match a REIT from config to fundamental data using fuzzy matching.
    """
    if not fundamental_data:
        return None
    
    name_key = normalize_reit_name(reit_name)
    
    # Direct match
    if name_key in fundamental_data:
        return fundamental_data[name_key]
    
    # Partial match - find best match
    best_match = None
    best_score = 0
    
    for key, data in fundamental_data.items():
        # Check if key words overlap
        name_words = set(name_key.split())
        key_words = set(key.split())
        overlap = len(name_words & key_words)
        
        if overlap > best_score:
            best_score = overlap
            best_match = data
    
    if best_score >= 2:  # At least 2 words must match
        return best_match
    
    return None


def fetch_reit_data(ticker, period="6mo"):
    """
    Fetches historical data for a given ticker.
    """
    try:
        logger.info(f"Fetching data for {ticker}...")
        stock = yf.Ticker(ticker)
        hist = stock.history(period=period)
        
        if hist.empty:
            logger.warning(f"No data found for {ticker}")
            return None
        
        return hist
    except Exception as e:
        logger.error(f"Error fetching data for {ticker}: {e}")
        return None


def get_current_price(ticker):
    """Get current price for a ticker."""
    try:
        stock = yf.Ticker(ticker)
        return stock.fast_info.last_price
    except:
        try:
            hist = stock.history(period="1d")
            if not hist.empty:
                return hist['Close'].iloc[-1]
        except:
            pass
        return 0.0


def get_sector_summary(reits_data):
    """
    Aggregate metrics by sector.
    Returns dict with avg yield, avg P/NAV, avg gearing per sector.
    """
    sector_data = {}
    
    for reit in reits_data:
        sector = reit.get('sector', 'Other')
        if sector not in sector_data:
            sector_data[sector] = {
                'yields': [],
                'pnavs': [],
                'gearings': [],
                'count': 0
            }
        
        sector_data[sector]['count'] += 1
        
        if reit.get('dividend_yield'):
            sector_data[sector]['yields'].append(reit['dividend_yield'])
        if reit.get('price_to_nav'):
            sector_data[sector]['pnavs'].append(reit['price_to_nav'])
        if reit.get('gearing_ratio'):
            sector_data[sector]['gearings'].append(reit['gearing_ratio'])
    
    # Calculate averages
    summary = {}
    for sector, data in sector_data.items():
        summary[sector] = {
            'count': data['count'],
            'avg_yield': round(sum(data['yields']) / len(data['yields']), 2) if data['yields'] else 0,
            'avg_pnav': round(sum(data['pnavs']) / len(data['pnavs']), 2) if data['pnavs'] else 0,
            'avg_gearing': round(sum(data['gearings']) / len(data['gearings']), 1) if data['gearings'] else 0,
        }
    
    return summary


# Sector mapping for REITs in config
SECTOR_MAPPING = {
    'Commercial/Retail': 'Commercial',
    'Industrial': 'Industrial',
    'Logistics': 'Logistics',
    'Industrial DC': 'Industrial',
    'Logistics/Commercial': 'Logistics',
    'Retail': 'Retail',
    'Data Centre': 'Data Centre',
    'Healthcare': 'Healthcare',
}

def get_sector_category(segment):
    """Map segment to broader sector category."""
    return SECTOR_MAPPING.get(segment, 'Other')
