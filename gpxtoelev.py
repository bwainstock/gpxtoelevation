# filename: gpxtoelev.py
# input: gpx file
# Parses gpx XML file to elevation profile using Google Elevation API

import math
import simplejson
import urllib
import pylab
from sys import argv
import gpolyencode

ELEVATION_BASE_URL = 'http://maps.google.com/maps/api/elevation/json'
script, filename = argv

def getElevation(path="", samples="100",sensor="false", **elvtn_args):

    # Google Elevation API call.  Takes lat/lon as input, outputs elevation dictionary.
    
    encpath = "enc:" + path
    #print "encpath: " + encpath
    elvtn_args.update({
        'path': encpath,
        'samples': samples,
        'sensor': sensor
    })

    url = ELEVATION_BASE_URL + '?' + urllib.urlencode(elvtn_args)
    #print "url: " , url
    response = simplejson.load(urllib.urlopen(url))
    #print "response: " , response
    # Create a dictionary for each results[] object
    elevationArray = []

    for resultset in response['results']:
        elevfeet = resultset['elevation'] * 3.281 # Convert elevation to feet
        elevationArray.append(elevfeet)
   
    responsefile = open("responsefile", "w")
    responsefile.write(str(response))
    responsefile.close()

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
            lat = float(line[latstart + 1:latend])
#            print lat

            lonstart = line.find('"', latend + 1)
            lonend = line.find('"', lonstart + 1)
            lon = float(line[lonstart + 1:lonend])
#            print lon

            pathdict.append((lat, lon))
    myPath = ''
    limit = 0

#    print pathdict

    for k, v in pathdict:
        myPath = myPath + str(k) + "," + str(v) + "|"
        limit = limit + 1

#    pathStr = myPath[:-1

    return pathdict

def distance(pathdict):
    # Haversine formula to calculate distance between GPS coordinates.
    # Written by Wayne Dyck
    
    dist = 0
    #print pathlist
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

        
#        print "lat: " , lat1
#        print "lon: " , lon1
#        print "dist: " , dist

    return dist

def polyEncoder(pathlist):

    encoder = gpolyencode.GPolyEncoder()
    codedpath = encoder.encode(pathlist)
    points = codedpath['points']
    #print "*" * 100
    #print codedpath
    #print len(points)

    return points

def elevPlot(y, xDist):

# Uses pylab to plot elevation data.

    # Fill xnums list with len(y) coords evenly spaced
    xnums = []
    incs = xDist / (len(y) - 1)
    for i in range(len(y)):
         xnums.append(i * incs)

    # Plot graph using pylab
    graphinfo = 'Distance: ' + ("%.2f" % xDist)
    print "graphinfo: " , graphinfo
    pylab.xlim(0.0, xDist)
    pylab.plot(xnums, y, label= (graphinfo + ' mi'))
    pylab.legend()
    pylab.xlabel('Miles')
    pylab.ylabel('Feet')
    pylab.grid(True)
    pylab.title('Elevation Profile')
    pylab.show()
   
if __name__ == '__main__':
  
    pathlist = latLonPath(filename)

    pathStr = polyEncoder(pathlist)
    xdist = distance(pathlist)
    ycoord = getElevation(pathStr)

    elevPlot(ycoord, xdist)

    #print distance(pathlist)
    #print "ycoord: " , ycoord
