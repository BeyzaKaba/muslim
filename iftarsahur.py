from flask import Flask, render_template
import requests
import re
import json
from datetime import datetime, timedelta

app = Flask(__name__)

BASE_URL = "https://namazvakitleri.diyanet.gov.tr/tr-TR/{}/{}-icin-namaz-vakti"
CITY_IDS = {
    "istanbul": 9541,
    "ankara": 9531,
    "izmir": 9521,
    "bursa": 9511
}

def get_prayer_times(city):
    idler = json.load(open('ilceid.json'))
    city= city.replace("ç", "c").replace("ğ", "g").replace("ü", "u").replace("ı", "i").replace("ö", "o").replace("ş", "s") 
    il = city.upper() 
    ilce = city.upper()
    print(il)
    try:
        city_id = idler[il][ilce]
    except:
        city_id = idler["ISTANBUL"]["ISTANBUL"] 
    url = BASE_URL.format(city_id, city.capitalize())
    response = requests.get(url)
    page_content = response.text
    
    times = {}
    
    imsak_match = re.search(r'var _imsakTime = "(\d{2}:\d{2})";', page_content)
    aksam_match = re.search(r'var _aksamTime = "(\d{2}:\d{2})";', page_content)
    city_match = re.search(r'var srSehirAdi = "([^"]+)";', page_content)
    
    if imsak_match:
        times["imsak"] = imsak_match.group(1)
    if aksam_match:
        times["aksam"] = aksam_match.group(1)
    city_name = city_match.group(1) if city_match else city.capitalize()
    
    return times, city_name

def time_until(prayer_time):
    now = datetime.now()
    prayer_dt = datetime.strptime(prayer_time, "%H:%M").replace(year=now.year, month=now.month, day=now.day)
    if prayer_dt < now:
        prayer_dt += timedelta(days=1)
    remaining = prayer_dt - now
    
    return remaining

@app.route('/')
@app.route('/<city>')
def index(city="ISTANBUL"):
    prayer_times, city_name = get_prayer_times(city)
    iftar_remaining = time_until(prayer_times["aksam"])
    sahur_remaining = time_until(prayer_times["imsak"])
    return render_template("index.html", city=city_name, iftar_remaining=iftar_remaining.total_seconds(), sahur_remaining=sahur_remaining.total_seconds())

if __name__ == "__main__":
    app.run(debug=True)
