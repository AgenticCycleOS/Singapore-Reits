import os
import logging
from telegram import Bot
from telegram.constants import ParseMode
import asyncio

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TELEGRAM_BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHAT_ID = os.environ.get('TELEGRAM_CHAT_ID')

async def send_telegram_update(reits_data, portfolio_metrics=None, ai_analysis=None):
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
        
        # AI Market Commentary (New)
        if ai_analysis and ai_analysis.get('market_commentary'):
            commentary = ai_analysis['market_commentary']
            # Take only the first two sections or up to 200 chars for brevity
            preview = commentary.split('\n\n')[0] if '\n\n' in commentary else commentary[:200]
            message += f"🤖 *AI Insight:*\n_{preview}_\n\n"
        
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
        
        # AI Portfolio recommendation (New)
        if ai_analysis and ai_analysis.get('portfolio_recommendation'):
            rec = ai_analysis['portfolio_recommendation']
            stance = "Neutral"
            if "Overweight" in rec: stance = "🟢 Overweight"
            elif "Underweight" in rec: stance = "🔴 Underweight"
            message += f"\n🎯 *AI Stance:* {stance}\n"
        
        message += "\n🔗 [View Full AI Dashboard](https://agenticcycleos.github.io/Singapore-Reits/)"
        
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

def send_update(reits_data, portfolio_metrics=None, ai_analysis=None):
    """Synchronous wrapper for sending Telegram update."""
    return asyncio.run(send_telegram_update(reits_data, portfolio_metrics, ai_analysis))
