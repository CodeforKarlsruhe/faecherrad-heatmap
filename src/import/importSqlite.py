import glob
import pandas as pd
import sqlite3 as sql
import xml.etree.ElementTree as ET

from datetime import datetime

bike_info = {}

def addBikeInfo( bike_id, info ):
    if not bike_id in bike_info:
        bike_info[bike_id] = []
    bike_info[bike_id] = bike_info[bike_id] + [info]


importFiles = glob.glob("*.xml")

infos = []
spots = []
for fimport in importFiles:

    ts = fimport.split("-")[1].split(".")[0]

    tree = ET.parse(fimport)
    root = tree.getroot()

    #print root
    xCountry = root.find("country")
    xCity = xCountry.find("city")

    timestamp = 23

    for xPlace in xCity:

        isSpot = xPlace.get("spot") == "1"
        isBike = xPlace.get("bike") == "1"

        lat = float(xPlace.get("lat"))
        lng = float(xPlace.get("lng"))

        name = xPlace.get("name")
        ## bikes not in station have no meaningful names ...
        if isBike:
            name = ""

        if isSpot:
            spots.append((name, ts, xPlace.get("bikes")[0], lat, lng))

        s = xPlace.get("bike_numbers")
        if not s == None:
            bikesAtSpot = s.split(",")
            #print bikesAtSpot
            for bike in bikesAtSpot:
                addBikeInfo( bike, (ts,lat,lng, name, isSpot) )
                infos.append((int(bike), int(ts),lat,lng, name, isSpot))

# export as sqlite
df = pd.DataFrame(infos, columns=("BikeID", "Timestamp", "Lat", "Lng", "Name", "isSpot"))
db = sql.connect("db.sqlite")
df.to_sql('bikes', db, if_exists='replace')
df.to_csv('bikes.csv', index=False, encoding='utf8')
df['time'] = list(map(datetime.fromtimestamp, df.Timestamp.values))
df['period'] = df.time.dt.to_period('T')
_1minago = df.copy()
_1minago['period'] = (df.time - pd.Timedelta(60000000000)).dt.to_period('T')
_1minago = _1minago[['BikeID', 'Lat', 'Lng', 'Name', 'period']]
_1minnext = df.copy()
_1minnext['period'] = (df.time + pd.Timedelta(60000000000)).dt.to_period('T')
_1minnext = _1minnext[['BikeID', 'Lat', 'Lng', 'Name', 'period']]
time_border = pd.merge(_1minago, _1minnext, on=('BikeID', 'period'), how='inner')
time_border = time_border.query('(Lat_x == Lat_y) & (Lng_y == Lng_y)')
df = pd.merge(df, time_border, on=('BikeID', 'period'), how="left")
df = df[~((df['Lat'] == df['Lat_x']) & (df['Lng'] == df['Lng_x']))]
df = df[['BikeID', 'Timestamp', 'Lat', 'Lng', 'Name', 'isSpot']]
df.to_csv('bikes-sparse.csv', index=False, encoding='utf8')

bike_info =  {}
def bike_tuples(x):
    key = x.BikeID.values[0]
    x = x[['Timestamp', 'Lat', 'Lng', 'Name', 'isSpot']]
    bike_info[str(key)] = list(map(lambda x: list(x[1].values), x.iterrows()))

df.groupby('BikeID').apply(bike_tuples)

# dump as json file
import json
with open('db.json', 'w') as outfile:
     json.dump(bike_info, outfile, sort_keys=True, indent=4, ensure_ascii=False)


df = pd.DataFrame(spots, columns=("name", "timestamp", "bikes", "lat", "long"))
df.to_csv('spots.csv', index=False, encoding='utf-8')

