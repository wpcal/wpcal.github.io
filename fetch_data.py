import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import json

# Define the operating hours for each day of the week
OPERATING_HOURS = {
    'Monday': ('6:30 AM', '11:00 PM'),
    'Tuesday': ('6:30 AM', '11:00 PM'),
    'Wednesday': ('6:30 AM', '11:00 PM'),
    'Thursday': ('6:30 AM', '11:00 PM'),
    'Friday': ('6:30 AM', '9:00 PM'),
    'Saturday': ('8:00 AM', '8:00 PM'),
    'Sunday': ('8:00 AM', '9:00 PM')
}

def parse_time(time_str):
    """
    Parse time string to datetime object.
    """
    time_str = time_str.strip()
    try:
        return datetime.strptime(time_str, '%I:%M %p')
    except ValueError:
        try:
            return datetime.strptime(time_str, '%I:%M%p')
        except ValueError:
            # Try without leading zero
            return datetime.strptime('0' + time_str, '%I:%M %p')

def fetch_events(date):
    """
    Fetch events from the WPEC Calendar for the given date.
    """
    url = 'https://25livepub.collegenet.com/events-calendar/ga/atlanta/emory-wpec/woodpec/woodruff/25live-woodpec-cal'
    try:
        response = requests.get(url)
        response.raise_for_status()
        html_content = response.text
        
        soup = BeautifulSoup(html_content, 'html.parser')
        
        events = []
        for event in soup.find_all('div', class_='vevent'):
            dtstart = event.find('abbr', class_='dtstart')
            dtend = event.find('abbr', class_='dtend')
            
            if dtstart and dtend:
                event_datetime_str = dtstart.text.strip()
                event_end_time_str = dtend.text.strip()
                
                if date.strftime('%B') in event_datetime_str and str(date.day) in event_datetime_str:
                    location_elem = event.find('span', class_='location')
                    if location_elem:
                        location_text = location_elem.text
                        
                        if 'Court #3' in location_text or 'Court 3' in location_text:
                            start_time = event_datetime_str.split(',')[-1].strip()
                            end_time = event_end_time_str.rstrip('.')
                            events.append((start_time, end_time))
        
        return events
    except requests.RequestException as e:
        print(f"Error fetching event data: {e}")
        return []

def get_available_times(date):
    """
    Get available time slots for Court #3 on the given date.
    """
    day_name = date.strftime('%A')
    open_time_str, close_time_str = OPERATING_HOURS[day_name]
    open_time = datetime.combine(date, parse_time(open_time_str).time())
    close_time = datetime.combine(date, parse_time(close_time_str).time())

    events = fetch_events(date)
    
    if not events:
        # If no events found, create 2-hour slots for the entire day
        available_times = []
        current = open_time
        while current + timedelta(hours=2) <= close_time:
            available_times.append((current, current + timedelta(hours=2)))
            current += timedelta(hours=2)
        return available_times
    
    # Parse the event times
    parsed_events = []
    for start, end in events:
        try:
            start_dt = datetime.combine(date, parse_time(start).time())
            end_dt = datetime.combine(date, parse_time(end).time())
            parsed_events.append((start_dt, end_dt))
        except ValueError as e:
            print(f"Error parsing event time: {start} - {end}: {e}")
    
    parsed_events.sort()

    # Find gaps between events and convert to 2-hour slots
    available_times = []
    current_time = open_time

    for start, end in parsed_events:
        # Check if there's at least 2 hours before the next event
        while current_time + timedelta(hours=2) <= start:
            available_times.append((current_time, current_time + timedelta(hours=2)))
            current_time += timedelta(hours=2)
        current_time = max(current_time, end)

    # Check for availability after the last event
    while current_time + timedelta(hours=2) <= close_time:
        available_times.append((current_time, current_time + timedelta(hours=2)))
        current_time += timedelta(hours=2)

    return available_times

def fetch_availability_data():
    """
    Fetch availability data for the next 7 days and format it as a JSON structure.
    Returns a dictionary with dates as keys and available time slots as values.
    """
    try:
        availability_data = {}
        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        
        for i in range(7):
            date = today + timedelta(days=i)
            date_str = date.strftime("%Y-%m-%d")
            
            available_slots = []
            available_times = get_available_times(date)
            
            for start, end in available_times:
                slot = f"{start.strftime('%H:%M')}-{end.strftime('%H:%M')}"
                available_slots.append(slot)
            
            availability_data[date_str] = available_slots
        
        result = {
            "availability": availability_data,
            "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        return result
    except Exception as e:
        print(f"Error generating availability data: {e}")
        return {"availability": {}, "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

def save_availability_to_file(filename="data/availability.json"):
    """
    Save the availability data to a JSON file.
    """
    try:
        data = fetch_availability_data()
        with open(filename, 'w') as f:
            json.dump(data, f)
        print(f"Availability data saved to {filename}")
        return data
    except Exception as e:
        print(f"Error saving availability data: {e}")
        return None

if __name__ == '__main__':
    # Example usage:
    data = fetch_availability_data()
    print(json.dumps(data, indent=2))
    
    # Uncomment to save to file:
    save_availability_to_file()
