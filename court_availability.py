import os
import json
import time
from datetime import datetime, timedelta
import schedule
import requests
from flask import Flask, render_template_string
from fetch_data import fetch_availability_data, save_availability_to_file

# Configuration
REPO_NAME = "court-availability"
DATA_FILE = "data/availability.json"
HTML_FILE = "index.html"

# # Sample data structure - replace with your actual data source
# def fetch_availability_data():
#     """
#     Fetch availability data from your source.
#     In a real implementation, this would call an API.
#     """
#     try:
#         # Replace this with your actual API call
#         # response = requests.get("https://your-api-endpoint.com/availability")
#         # if response.status_code == 200:
#         #     return response.json()
        
#         # For demo purposes, we'll return mock data
#         mock_data = {}
#         today = datetime.now()
        
#         for i in range(7):
#             date = today + timedelta(days=i)
#             date_str = date.strftime("%Y-%m-%d")
            
#             # Generate some random availability slots
#             available_slots = []
#             start_hour = 8
#             for hour in range(start_hour, 22, 2):
#                 # Randomly decide if slot is available (70% chance)
#                 if hash(f"{date_str}-{hour}") % 10 < 7:
#                     available_slots.append(f"{hour}:00-{hour+2}:00")
            
#             mock_data[date_str] = available_slots
            
#         return mock_data
#     except Exception as e:
#         print(f"Error fetching data: {e}")
#         return {}

# def save_data(data):
#     """Save the fetched data to a JSON file."""
#     os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
#     with open(DATA_FILE, 'w') as f:
#         json.dump({
#             "availability": data,
#             "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
#         }, f)
#     print(f"Data saved at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

def generate_html():
    """Generate the HTML page using the saved data."""
    try:
        with open(DATA_FILE, 'r') as f:
            data = json.load(f)
        
        availability = data["availability"]
        last_updated = data["last_updated"]
        
        # Generate dates for the next 7 days
        today = datetime.now()
        dates = []
        for i in range(7):
            date = today + timedelta(days=i)
            date_str = date.strftime("%Y-%m-%d")
            date_display = date.strftime("%A %m-%d-%Y")
            dates.append({
                "date_str": date_str,
                "display": date_display,
                "slots": availability.get(date_str, [])
            })
        
        # HTML template
        html_template = """
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <meta http-equiv="refresh" content="900"> <!-- Refresh every 15 minutes -->
            <title>Woodpec PE Court #3 Availability</title>
            <style>
                body {
                    font-family: Arial, sans-serif;
                    max-width: 1000px;
                    margin: 0 auto;
                    padding: 20px;
                    line-height: 1.6;
                }
                h1 {
                    text-align: center;
                    color: #2c3e50;
                }
                .updated {
                    text-align: center;
                    font-style: italic;
                    color: #7f8c8d;
                    margin-bottom: 20px;
                }
                .day-container {
                    margin-bottom: 30px;
                    border: 1px solid #ddd;
                    border-radius: 5px;
                    padding: 15px;
                }
                h2 {
                    margin-top: 0;
                    color: #3498db;
                    border-bottom: 1px solid #eee;
                    padding-bottom: 10px;
                }
                .slots {
                    display: flex;
                    flex-wrap: wrap;
                    gap: 10px;
                }
                .slot {
                    background-color: #2ecc71;
                    color: white;
                    padding: 8px 12px;
                    border-radius: 4px;
                    display: inline-block;
                }
                .no-slots {
                    color: #e74c3c;
                    font-style: italic;
                }
                @media (max-width: 600px) {
                    body {
                        padding: 10px;
                    }
                    .day-container {
                        padding: 10px;
                    }
                }
            </style>
        </head>
        <body>
            <h1>Woodpec PE Court #3 Availability</h1>
            <p class="updated">Last updated: {{ last_updated }}</p>
            
            {% for day in dates %}
            <div class="day-container">
                <h2>{{ day.display }}</h2>
                <div class="slots">
                    {% if day.slots %}
                        {% for slot in day.slots %}
                            <div class="slot">{{ slot }}</div>
                        {% endfor %}
                    {% else %}
                        <p class="no-slots">No available slots</p>
                    {% endif %}
                </div>
            </div>
            {% endfor %}
            <footer class="byline">Coded by Claude 3.7, prompted by <a href="https://toan-vt.github.io" target="_blank">Toan Tran</a> | I am not responsible for any errors in court availability information :) | Created on a random boring day :) March 3, 2025 | </footer>
            <script>
                // This script will update the page every 15 minutes
                setTimeout(function() {
                    window.location.reload();
                }, 15 * 60 * 1000);
            </script>
        </body>
        </html>
        """
        
        # Render the template with the data
        from jinja2 import Template
        template = Template(html_template)
        rendered_html = template.render(dates=dates, last_updated=last_updated)
        
        # Write the HTML to file
        with open(HTML_FILE, 'w') as f:
            f.write(rendered_html)
            
        print(f"HTML generated at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
    except Exception as e:
        print(f"Error generating HTML: {e}")

def update_data():
    """Fetch new data and update the website."""
    data = fetch_availability_data()
    # save_data(data)
    save_availability_to_file()
    generate_html()

# GitHub Pages deployment function (run separately or as needed)
def setup_github_pages():
    """
    Sets up GitHub Pages repository for deployment.
    This would typically be done once manually.
    """
    commands = [
        f"git init",
        f"git add {HTML_FILE} {DATA_FILE}",
        f'git commit -m "Update court availability"',
        f"git branch -M main",
        f"git remote add origin https://github.com/yourusername/{REPO_NAME}.git",
        f"git push -u origin main"
    ]
    
    print("GitHub Pages setup commands:")
    for cmd in commands:
        print(f"  {cmd}")

# GitHub Pages update function (for scheduled updates)
def update_github_pages():
    """
    Updates the GitHub Pages repository with new data.
    This can be scheduled to run after each data update.
    """
    commands = [
        f"git add {HTML_FILE} {DATA_FILE}",
        f'git commit -m "Update court availability {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}"',
        f"git push origin main"
    ]
    
    print("Running GitHub Pages update:")
    for cmd in commands:
        print(f"  {cmd}")
        # In a real implementation, you would use subprocess to run these commands
        # import subprocess
        # subprocess.run(cmd, shell=True)

# Web server for local testing
def run_local_server():
    app = Flask(__name__)
    
    @app.route('/')
    def home():
        with open(HTML_FILE, 'r') as f:
            return f.read()
    
    app.run(debug=True, port=8000)

# Main execution
if __name__ == "__main__":
    # Initial data fetch and page generation
    update_data()
    
    # Schedule regular updates every 15 minutes
    schedule.every(15).minutes.do(update_data)
    
    # Optional: Schedule GitHub Pages updates
    schedule.every(15).minutes.do(update_github_pages)
    
    # Run scheduler in a loop
    print("Starting scheduler. Press Ctrl+C to exit.")
    try:
        while True:
            schedule.run_pending()
            time.sleep(1)
    except KeyboardInterrupt:
        print("Scheduler stopped.")
