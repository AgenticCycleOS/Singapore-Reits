from jinja2 import Environment, FileSystemLoader
import os
from datetime import datetime

def generate_dashboard(reits_data, output_file="index.html"):
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
    
    # Context data for template
    context = {
        "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "reits": reits_data,
        "top_gainer": top_gainer,
        "top_loser": top_loser
    }
    
    # Render
    html_content = template.render(context)
    
    # write to file
    with open(output_file, "w", encoding='utf-8') as f:
        f.write(html_content)
        
    print(f"Dashboard generated at {output_file}")
