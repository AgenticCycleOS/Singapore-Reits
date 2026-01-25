import requests
import os
import logging

logger = logging.getLogger(__name__)

def send_telegram_summary(reits_data):
    """
    Sends a summary of the REITs performance to Telegram.
    """
    token = os.environ.get("TELEGRAM_TOKEN")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID")
    
    if not token or not chat_id:
        logger.warning("Telegram token or chat ID not set. Skipping notification.")
        return

    # Sort to find movers
    sorted_by_change = sorted(reits_data, key=lambda x: x['change_pct'], reverse=True)
    top_3 = sorted_by_change[:3]
    bottom_3 = sorted_by_change[-3:]
    
    # Construct Message
    message = "<b>ðŸ‡¸ðŸ‡¬ Weekly S-REITs Update</b>\n\n"
    
    message += "<b>ðŸš€ Top Gainer:</b>\n"
    message += f"{top_3[0]['name']}: {top_3[0]['change_pct']}%\n\n"
    
    message += "<b>ðŸ”¥ Key Movers:</b>\n"
    for r in top_3:
        message += f"âœ… {r['ticker']}: +{r['change_pct']}%\n"
    message += "\n"
    for r in bottom_3:
        if r['change_pct'] < 0:
            message += f"ðŸ”» {r['ticker']}: {r['change_pct']}%\n"
            
    message += "\n<b>ðŸš¦ Signals:</b>\n"
    alerts = [r for r in reits_data if "Opportunity" in " ".join(r['insights']) or "Risk" in " ".join(r['insights'])]
    if alerts:
        for a in alerts[:5]: # Limit to 5 alerts
            insight = [i for i in a['insights'] if "Opportunity" in i or "Risk" in i][0]
            icon = "ðŸŸ¢" if "Opportunity" in insight else "ðŸ”´"
            message += f"{icon} {a['ticker']}: {insight}\n"
    else:
        message += "No major technical signals this week.\n"
        
    message += "\n<a href='https://lew-family.github.io/s-reits-dashboard/'>View Full Dashboard</a>"
    
    # Send
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "HTML"
    }
    
    try:
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            logger.info("Telegram message sent successfully.")
        else:
            logger.error(f"Failed to send Telegram message: {response.text}")
    except Exception as e:
        logger.error(f"Error sending Telegram message: {e}")
