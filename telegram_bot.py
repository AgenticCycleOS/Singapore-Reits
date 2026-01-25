import os
import logging
from telegram import Bot
from telegram.constants import ParseMode
import asyncio

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TELEGRAM_BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHAT_ID = os.environ.get('TELEGRAM_CHAT_ID')

async def send_telegram_update(reits_data, portfolio_metrics=None):
    """
    Sends a formatted update to Telegram.
    """
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        logger.warning("Telegram credentials not configured")
        return False
    
    try:
        bot = Bot(token=TELEGRAM_BOT_TOKEN)
        
        # Sort for top/bottom performers
        sorted_data = sorted(reits_data, key=lambda x: x['change_pct'], reverse=True)
        top_3 = sorted_data[:3]
        bottom_3 = sorted_data[-3:]
        
        # Build message
        message = "🇸🇬 *S-REITs Weekly Update*\n\n"
        
        # Portfolio summary
        if portfolio_metrics:
            message += "*Portfolio Averages:*\n"
            message += f"📊 Yield: {portfolio_metrics.get('avg_yield', 'N/A')}%\n"
            message += f"📈 P/NAV: {portfolio_metrics.get('avg_pnav', 'N/A')}x\n"
            message += f"⚖️ Gearing: {portfolio_metrics.get('avg_gearing', 'N/A')}%\n\n"
        
        # Top performers
        message += "*🟢 Top Performers:*\n"
        for reit in top_3:
            yield_str = f" | Yield: {reit['dividend_yield']}%" if reit.get('dividend_yield') else ""
            message += f"• {reit['name'][:25]}: +{reit['change_pct']}%{yield_str}\n"
        
        message += "\n*🔴 Decliners:*\n"
        for reit in bottom_3:
            yield_str = f" | Yield: {reit['dividend_yield']}%" if reit.get('dividend_yield') else ""
            message += f"• {reit['name'][:25]}: {reit['change_pct']}%{yield_str}\n"
        
        # High yield alerts
        high_yield_reits = [r for r in reits_data if r.get('dividend_yield') and r['dividend_yield'] >= 7]
        if high_yield_reits:
            message += "\n*💰 High Yield Alerts (≥7%):*\n"
            for reit in sorted(high_yield_reits, key=lambda x: x['dividend_yield'], reverse=True)[:3]:
                message += f"• {reit['name'][:25]}: {reit['dividend_yield']}%\n"
        
        # Deep discount alerts
        deep_discount = [r for r in reits_data if r.get('price_to_nav') and r['price_to_nav'] < 0.8]
        if deep_discount:
            message += "\n*🏷️ Deep NAV Discounts (<0.8x):*\n"
            for reit in sorted(deep_discount, key=lambda x: x['price_to_nav'])[:3]:
                message += f"• {reit['name'][:25]}: {reit['price_to_nav']}x P/NAV\n"
        
        # Technical alerts
        oversold = [r for r in reits_data if r.get('rsi') and r['rsi'] < 30]
        overbought = [r for r in reits_data if r.get('rsi') and r['rsi'] > 70]
        
        if oversold:
            message += "\n*📉 Oversold (RSI<30):*\n"
            for reit in oversold:
                message += f"• {reit['name'][:25]}: RSI {reit['rsi']}\n"
        
        if overbought:
            message += "\n*📈 Overbought (RSI>70):*\n"
            for reit in overbought:
                message += f"• {reit['name'][:25]}: RSI {reit['rsi']}\n"
        
        message += "\n🔗 [View Dashboard](https://agenticcycleos.github.io/Singapore-Reits/)"
        
        await bot.send_message(
            chat_id=TELEGRAM_CHAT_ID,
            text=message,
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=True
        )
        
        logger.info("Telegram update sent successfully")
        return True
        
    except Exception as e:
        logger.error(f"Error sending Telegram update: {e}")
        return False

def send_update(reits_data, portfolio_metrics=None):
    """Synchronous wrapper for sending Telegram update."""
    return asyncio.run(send_telegram_update(reits_data, portfolio_metrics))
