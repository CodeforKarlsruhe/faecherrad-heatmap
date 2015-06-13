



import xml.etree.ElementTree as ET
import glob

bike_info = {}

def addBikeInfo( bike_id, info ):
    if not bike_id in bike_info:
        bike_info[bike_id] = []
    bike_info[bike_id] = bike_info[bike_id] + [info]


importFiles = glob.glob("*.xml")
#print importFiles

for fimport in importFiles:

    ts = fimport.split("-")[1].split(".")[0]
    #print ts

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

        s = xPlace.get("bike_numbers")
        if not s == None:
            bikesAtSpot = s.split(",")
            #print bikesAtSpot
            for bike in bikesAtSpot:
                addBikeInfo( bike, (ts,lat,lng, name, isSpot) )

#for (k,bi) in bike_info.iteritems():
#    print len(bi)

import json
print json.dumps(bike_info)



