import string

from flask import Flask
from flask import render_template
from metar import Metar
import xml.etree.ElementTree as ET


try:
    from urllib2 import urlopen
except:
    from urllib.request import urlopen

BASE_URL = "http://tgftp.nws.noaa.gov/data/observations/metar/stations"

app = Flask(__name__)

def fetch_metar(name):
    url = "%s/%s.TXT" % (BASE_URL, name)
    try:
        urlh = urlopen(url)
        report = ""
        for line in urlh:
            if not isinstance(line, str):
                line = line.decode()  # convert Python3 bytes buffer to string
            if line.startswith(name):
                report = line.strip()
                return Metar.Metar(line)
        if not report:
            print("No data for ", name, "\n\n")
    except Metar.ParserError as exc:
        print("METAR code: ", line)
        print(string.join(exc.args, ", "), "\n")
    except:
        import traceback
        print(traceback.format_exc())
        print("Error retrieving", name, "data", "\n")

def fetch_flight_cat(station):
    url = "https://www.aviationweather.gov/adds/dataserver_current/httpparam?dataSource=metars&requestType=retrieve&format=xml&hoursBeforeNow=5&mostRecentForEachStation=true&stationString=" + station
    try:
        urlh = urlopen(url)
        data = urlh.read().decode()
        x = ET.fromstring(data)
        return x.find('data').find('METAR').find('flight_category').text
    except:
        import traceback
        print(traceback.format_exc())
        print("Error retrieving", station, "data", "\n")

@app.route("/")
def dashboard():
    m = fetch_metar('KDAB')
    flight_cat = fetch_flight_cat('KDAB')
    print(m)
    return render_template('dashboard.html', airport='KDAB', metar=m, flight_cat=flight_cat)

@app.route("/<identifier>")
def dashboard_other_airport(identifier):
    airport = identifier.upper()
    flight_cat = fetch_flight_cat(airport)
    return render_template('dashboard.html', airport=airport, metar=fetch_metar(airport), flight_cat=flight_cat)

app.run(host="0.0.0.0", debug=True)