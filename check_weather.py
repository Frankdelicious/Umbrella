import os
import requests
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

def get_weather():
    api_key = os.environ['OPENWEATHER_API_KEY']
    lat = os.environ['LATITUDE']
    lon = os.environ['LONGITUDE']
    
    url = f"https://api.openweathermap.org/data/3.0/onecall"
    params = {
        "lat": lat,
        "lon": lon,
        "appid": api_key,
        "exclude": "minutely,hourly,alerts",
        "units": "metric"
    }
    
    response = requests.get(url, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Error fetching weather data: {response.status_code}")

def should_bring_umbrella(weather_data):
    # Check current weather and next few hours
    current_weather = weather_data['current']
    daily_forecast = weather_data['daily'][0]  # Today's forecast
    
    # Weather condition codes that indicate rain
    rain_conditions = range(200, 600)  # Weather codes 200-599 are various forms of precipitation
    
    current_condition = current_weather['weather'][0]['id']
    pop = daily_forecast.get('pop', 0)  # Probability of precipitation
    
    return current_condition in rain_conditions or pop > 0.3  # 30% chance of rain threshold

def send_email(needs_umbrella):
    sender_email = os.environ['EMAIL_ADDRESS']
    sender_password = os.environ['EMAIL_PASSWORD']
    receiver_email = os.environ['EMAIL_ADDRESS']  # Sending to self
    
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg['Subject'] = "☂️ Daily Weather Update"
    
    if needs_umbrella:
        body = "You should bring an umbrella today! There's a good chance of rain."
    else:
        body = "No need for an umbrella today! The weather looks clear."
    
    msg.attach(MIMEText(body, 'plain'))
    
    try:
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.send_message(msg)
    except Exception as e:
        print(f"Error sending email: {e}")
        raise

def main():
    try:
        weather_data = get_weather()
        needs_umbrella = should_bring_umbrella(weather_data)
        send_email(needs_umbrella)
    except Exception as e:
        print(f"Error in weather check: {e}")
        raise

if __name__ == "__main__":
    main()