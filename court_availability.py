import os
import json
import time
from datetime import datetime, timedelta
import requests
from flask import Flask, render_template_string
from fetch_data import save_availability_to_file
import subprocess

# Configuration
REPO_NAME = "court-availability"
DATA_FILE = "data/availability.json"
HTML_FILE = "index.html"

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
            <footer class="byline">Coded by Claude 3.7 & GPT4, prompted <a href="https://toan-vt.github.io" target="_blank">Toan Tran</a>, deployed by Github | I am not responsible for any errors in court availability information :) | Created in a random boring evening :) March 3, 2025 </footer>
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
    save_availability_to_file()
    generate_html()
    commit_and_push_changes()

def commit_and_push_changes():
    """Commit and push changes to GitHub."""
    subprocess.run(["git", "add", HTML_FILE, DATA_FILE])
    subprocess.run(["git", "commit", "-m", f"Update court availability {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"])
    subprocess.run(["git", "push", "origin", "main"])

if __name__ == "__main__":
    # Initial data fetch and page generation
    update_data()
