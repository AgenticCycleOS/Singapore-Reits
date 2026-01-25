"""
Claude API integration for AI-powered S-REIT analysis.
Generates market commentary, individual REIT insights, and sector outlooks.
"""

import os
import json
import logging
from anthropic import Anthropic

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

client = None

def init_client():
    global client
    api_key = os.environ.get('ANTHROPIC_API_KEY')
    if not api_key:
        logger.warning("ANTHROPIC_API_KEY not set - AI analysis disabled")
        return False
    client = Anthropic(api_key=api_key)
    return True


def generate_market_commentary(reits_data, portfolio_metrics, sector_summary):
    if not client and not init_client():
        return get_fallback_commentary(portfolio_metrics)
    
    data_summary = {
        "portfolio_metrics": portfolio_metrics,
        "sector_summary": sector_summary,
        "top_performers": sorted(reits_data, key=lambda x: x['change_pct'], reverse=True)[:3],
        "worst_performers": sorted(reits_data, key=lambda x: x['change_pct'])[:3],
        "high_yield": [r for r in reits_data if r.get('dividend_yield') and r['dividend_yield'] >= 6],
        "deep_discount": [r for r in reits_data if r.get('price_to_nav') and r['price_to_nav'] < 0.85],
        "high_gearing": [r for r in reits_data if r.get('gearing_ratio') and r['gearing_ratio'] >= 42],
        "oversold": [r for r in reits_data if r.get('rsi') and r['rsi'] < 35],
        "overbought": [r for r in reits_data if r.get('rsi') and r['rsi'] > 65],
    }
    
    prompt = f"""You are a Singapore REIT market analyst. Generate a concise weekly market commentary based on the following data.

DATA:
{json.dumps(data_summary, indent=2)}

CONTEXT:
- Singapore REITs must distribute 90% of taxable income
- MAS gearing limit is 50%
- Current interest rate environment affects REIT valuations
- P/NAV < 1 indicates trading below book value

Generate a market commentary with these sections (keep each section to 2-3 sentences):

1. **Weekly Overview**: Overall market sentiment and key moves
2. **Yield Analysis**: Commentary on current yield levels vs historical norms
3. **Valuation Check**: P/NAV analysis - are REITs cheap or expensive?
4. **Risk Watch**: Gearing concerns or interest rate sensitivity
5. **Actionable Insight**: One specific opportunity or risk to watch

Keep the tone professional but accessible. Focus on actionable insights for investors.
Total length: 150-200 words."""

    try:
        response = client.messages.create(
            model="claude-3-5-sonnet-20240620",
            max_tokens=500,
            messages=[{"role": "user", "content": prompt}]
        )
        return response.content[0].text
    except Exception as e:
        logger.error(f"Error generating market commentary: {e}")
        return get_fallback_commentary(portfolio_metrics)


def generate_reit_analysis(reit_data):
    if not client and not init_client():
        return None
    
    prompt = f"""Analyze this Singapore REIT and provide a brief investment perspective (2-3 sentences):

REIT: {reit_data['name']}
Sector: {reit_data.get('sector', 'N/A')}
Price: ${reit_data['price']}
Weekly Change: {reit_data['change_pct']}%
Dividend Yield: {reit_data.get('dividend_yield', 'N/A')}%
P/NAV: {reit_data.get('price_to_nav', 'N/A')}x
Gearing: {reit_data.get('gearing_ratio', 'N/A')}%
RSI: {reit_data.get('rsi', 'N/A')}
Trend: {reit_data.get('trend', 'N/A')}

Provide a concise assessment covering: valuation stance (undervalued/fair/overvalued), key risk, and outlook.
Keep response under 50 words."""

    try:
        response = client.messages.create(
            model="claude-3-5-sonnet-20240620",
            max_tokens=150,
            messages=[{"role": "user", "content": prompt}]
        )
        return response.content[0].text
    except Exception as e:
        logger.error(f"Error generating REIT analysis: {e}")
        return None


def generate_sector_outlook(sector_summary, reits_data):
    if not client and not init_client():
        return {}
    
    sector_reits = {}
    for reit in reits_data:
        sector = reit.get('sector', 'Other')
        if sector not in sector_reits:
            sector_reits[sector] = []
        sector_reits[sector].append({
            'name': reit['name'],
            'yield': reit.get('dividend_yield'),
            'pnav': reit.get('price_to_nav'),
            'change': reit['change_pct']
        })
    
    prompt = f"""Analyze Singapore REIT sectors and provide brief outlooks.

SECTOR DATA:
{json.dumps(sector_summary, indent=2)}

SECTOR REITS:
{json.dumps(sector_reits, indent=2)}

For each sector, provide a one-line outlook (bullish/neutral/bearish + reason).
Format as JSON: {{"sector_name": "outlook text"}}"""

    try:
        response = client.messages.create(
            model="claude-3-5-sonnet-20240620",
            max_tokens=400,
            messages=[{"role": "user", "content": prompt}]
        )
        text = response.content[0].text
        start = text.find('{')
        end = text.rfind('}') + 1
        if start >= 0 and end > start:
            return json.loads(text[start:end])
        return {}
    except Exception as e:
        logger.error(f"Error generating sector outlook: {e}")
        return {}


def generate_portfolio_recommendation(reits_data, portfolio_metrics):
    if not client and not init_client():
        return get_fallback_recommendation(portfolio_metrics)
    
    bullish_count = len([r for r in reits_data if r.get('trend') == 'Bullish'])
    bearish_count = len([r for r in reits_data if r.get('trend') == 'Bearish'])
    
    data = {
        "total_reits": len(reits_data),
        "bullish_count": bullish_count,
        "bearish_count": bearish_count,
        "neutral_count": len(reits_data) - bullish_count - bearish_count,
        "avg_yield": portfolio_metrics.get('avg_yield'),
        "avg_pnav": portfolio_metrics.get('avg_pnav'),
        "avg_gearing": portfolio_metrics.get('avg_gearing'),
        "top_yield_reit": max(reits_data, key=lambda x: x.get('dividend_yield', 0)),
        "best_value_reit": min([r for r in reits_data if r.get('price_to_nav')], 
                               key=lambda x: x.get('price_to_nav', 99), default=None),
    }
    
    prompt = f"""As a Singapore REIT analyst, provide a portfolio recommendation based on this data:

{json.dumps(data, indent=2, default=str)}

Provide:
1. **Overall Stance**: Overweight / Neutral / Underweight S-REITs (one word + one sentence reason)
2. **Top Pick**: Which REIT looks most attractive and why (one sentence)
3. **Avoid**: Any REIT showing warning signs (one sentence)
4. **Strategy**: One tactical suggestion for the week ahead

Keep total response under 100 words. Be specific and actionable."""

    try:
        response = client.messages.create(
            model="claude-3-5-sonnet-20240620",
            max_tokens=300,
            messages=[{"role": "user", "content": prompt}]
        )
        return response.content[0].text
    except Exception as e:
        logger.error(f"Error generating portfolio recommendation: {e}")
        return get_fallback_recommendation(portfolio_metrics)


def get_fallback_commentary(portfolio_metrics):
    avg_yield = portfolio_metrics.get('avg_yield', 5.0)
    avg_pnav = portfolio_metrics.get('avg_pnav', 1.0)
    avg_gearing = portfolio_metrics.get('avg_gearing', 38)
    
    yield_assessment = "attractive" if avg_yield >= 5.5 else "moderate" if avg_yield >= 4.5 else "compressed"
    value_assessment = "discount to NAV" if avg_pnav < 1 else "fair value" if avg_pnav < 1.1 else "premium"
    gearing_assessment = "elevated" if avg_gearing >= 42 else "comfortable" if avg_gearing >= 35 else "conservative"
    
    return f"""**Weekly Overview**: S-REITs showing mixed performance this week with sector rotation ongoing.

**Yield Analysis**: Portfolio average yield at {avg_yield}% remains {yield_assessment} versus historical norms of 5-6%.

**Valuation Check**: Average P/NAV of {avg_pnav}x indicates the sector is trading at {value_assessment}.

**Risk Watch**: Average gearing at {avg_gearing}% is {gearing_assessment}. Monitor interest rate sensitivity.

**Actionable Insight**: Focus on REITs with yields above 6% and P/NAV below 0.9x for value opportunities."""


def get_fallback_recommendation(portfolio_metrics):
    avg_pnav = portfolio_metrics.get('avg_pnav', 1.0)
    stance = "Neutral" if 0.95 <= avg_pnav <= 1.1 else "Overweight" if avg_pnav < 0.95 else "Underweight"
    
    return f"""**Overall Stance**: {stance} - Valuations are {"attractive" if avg_pnav < 1 else "stretched"} at current levels.

**Top Pick**: Focus on industrial and logistics REITs with structural demand tailwinds.

**Avoid**: REITs with gearing above 45% face refinancing risks in current rate environment.

**Strategy**: Accumulate quality names on weakness; avoid chasing momentum in overbought territory."""


def generate_full_analysis(reits_data, portfolio_metrics, sector_summary):
    logger.info("Generating AI analysis...")
    
    analysis = {
        'market_commentary': generate_market_commentary(reits_data, portfolio_metrics, sector_summary),
        'sector_outlook': generate_sector_outlook(sector_summary, reits_data),
        'portfolio_recommendation': generate_portfolio_recommendation(reits_data, portfolio_metrics),
        'ai_enabled': client is not None,
    }
    
    sorted_by_movement = sorted(reits_data, key=lambda x: abs(x['change_pct']), reverse=True)[:5]
    reit_analyses = {}
    for reit in sorted_by_movement:
        ai_analysis = generate_reit_analysis(reit)
        if ai_analysis:
            reit_analyses[reit['ticker']] = ai_analysis
    
    analysis['reit_analyses'] = reit_analyses
    
    logger.info(f"AI analysis complete. Generated {len(reit_analyses)} individual analyses.")
    return analysis
