from jinja2 import Environment, FileSystemLoader
import os
from datetime import datetime

def generate_dashboard(reits_data, output_file="index.html", sector_summary=None, portfolio_metrics=None):
    """
    Generates the HTML dashboard from the analyzed data.
    """
    # Setup Jinja2 environment
    env = Environment(loader=FileSystemLoader(searchpath="./templates"))
    template = env.get_template("index.html")
    
    # Sort data for summary
    sorted_by_change = sorted(reits_data, key=lambda x: x['change_pct'], reverse=True)
    top_gainer = sorted_by_change[0] if sorted_by_change else None
    top_loser = sorted_by_change[-1] if sorted_by_change else None
    
    # Sort by yield for yield leaders
    reits_with_yield = [r for r in reits_data if r.get('dividend_yield')]
    sorted_by_yield = sorted(reits_with_yield, key=lambda x: x['dividend_yield'], reverse=True)
    highest_yield = sorted_by_yield[0] if sorted_by_yield else None
    
    # Sort by P/NAV for value plays
    reits_with_pnav = [r for r in reits_data if r.get('price_to_nav')]
    sorted_by_pnav = sorted(reits_with_pnav, key=lambda x: x['price_to_nav'])
    deepest_discount = sorted_by_pnav[0] if sorted_by_pnav else None
    
    # Default portfolio metrics
    if portfolio_metrics is None:
        portfolio_metrics = {
            'avg_yield': 0,
            'avg_pnav': 0,
            'avg_gearing': 0,
        }
    
    # Context data for template
    context = {
        "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "reits": reits_data,
        "top_gainer": top_gainer,
        "top_loser": top_loser,
        "highest_yield": highest_yield,
        "deepest_discount": deepest_discount,
        "sector_summary": sector_summary or {},
        "portfolio_metrics": portfolio_metrics,
        "total_reits": len(reits_data),
    }
    
    # Render
    html_content = template.render(context)
    
    # Ensure public directory exists
    output_dir = "public"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    output_path = os.path.join(output_dir, output_file)
    
    # Write to file
    with open(output_path, "w", encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"Dashboard generated at {output_path}")
