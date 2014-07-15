# filename: gpxtoelev.py
# input: gpx file
# Parses gpx XML file to elevation profile using Google Elevation API

import math
import simplejson
import urllib
import pylab
from sys import argv

ELEVATION_BASE_URL = 'http://maps.google.com/maps/api/elevation/json'
script, filename = argv

def getElevation(path="36.578581,-118.291994|36.23998,-116.83171",samples="100",sensor="false", **elvtn_args):

    # Google Elevation API call.  Takes lat/lon as input, outputs elevation dictionary.

    elvtn_args.update({
        'path': path,
        'samples': samples,
        'sensor': sensor
    })

    url = ELEVATION_BASE_URL + '?' + urllib.urlencode(elvtn_args)
    response = simplejson.load(urllib.urlopen(url))

    # Create a dictionary for each results[] object
    elevationArray = []

    responsefile = open("responsefile", "a")

    for resultset in response['results']:
      elevationArray.append(resultset['elevation'])
    
    return elevationArray  

def latLonPath(filename):

# Parses gpx file into Google Elevation API formated longitude and latitude.

    TRKPT = 'trkpt'

    pathdict = [] 
    f = open(filename)

    for line in f:
        if TRKPT in line:
            latstart = line.find('"')
            latend = line.find('"', latstart + 1)
            lat = line[latstart + 1:latend]
            print lat

            lonstart = line.find('"', latend + 1)
            lonend = line.find('"', lonstart + 1)
            lon = line[lonstart + 1:lonend]
            print lon

            pathdict.append((lat, lon))
    myPath = ''
    limit = 0

#    print pathdict

    for k, v in pathdict:
        myPath = myPath + k + "," + v + "|"
        limit = limit + 1

    pathStr = myPath[:-1]
    return pathStr, pathdict

def distance(pathdict):
    # Haversine formula to calculate distance between GPS coordinates.
    # Written by Wayne Dyck
    
    dist = 0
    print pathlist
    for item in range(len(pathlist) - 1):
        itemNum = 0
#        pathItems = pathdict
        lat1, lon1 = pathlist[item]
        lat2, lon2 = pathlist[item + 1]
        radius = 3959 # mi

        dlat = math.radians(float(lat2) - float(lat1))
        dlon = math.radians(float(lon2) - float(lon1))
        a = math.sin(dlat / 2) * math.sin(dlat / 2) + math.cos(math.radians(float(lat1))) \
         * math.cos(math.radians(float(lat2))) * math.sin(dlon / 2) * math.sin(dlon / 2)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        dist += radius * c

        
        print "lat: " , lat1
        print "lon: " , lon1
        print "dist: " , dist

    return dist

def elevPlot(y, xLimit):

# Uses pylab to plot elevation data.

    pylab.xlim(xLimit)
    pylab.plot(y)
    pylab.show()
   
if __name__ == '__main__':
  
    pathStr, pathlist = latLonPath(filename)
  
#    print pathStr
#    print "*" *100
#    pathItems = pathdict.items()
#    print pathItems[0]
    xlimit = distance(pathlist)

    print xlimit

    ycoord = getElevation(pathStr)
    elevPlot(ycoord, xlimit)
#    print distance(pathlist)
