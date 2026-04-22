import requests
import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("API_KEY")
city = os.getenv("CITY")

url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"

response = requests.get(url)
data = response.json()

print("===== DATA CUACA =====")
print("Kota  :", data["name"])
print("Suhu  :", data["main"]["temp"], "°C")
print("Cuaca :", data["weather"][0]["description"])