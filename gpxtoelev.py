# filename: gpxtoelev.py
# input: gpx file
# Parses gpx XML file to elevation profile using Google Elevation API

import math
import simplejson
import urllib
import pylab
import numpy
from sys import argv
import gpolyencode

ELEVATION_BASE_URL = 'http://maps.google.com/maps/api/elevation/json'
script, filename = argv

def getElevation(path="", samples="500",sensor="false", key="AIzaSyBB_e1H1aOubumnTfGDzjcyO3R9CXHK3q8", **elvtn_args):

    # Google Elevation API call.  Takes lat/lon as input, outputs elevation dictionary.
    
    encpath = "enc:" + path

    print "len path: " , len(path)

    elvtn_args.update({
        'path': encpath,
        'samples': samples,
        'sensor': sensor
    })

    url = ELEVATION_BASE_URL + '?' + urllib.urlencode(elvtn_args)

    print len(url)
    print "urllib: " , len(elvtn_args.values())

    response = simplejson.load(urllib.urlopen(url))
    
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

            lonstart = line.find('"', latend + 1)
            lonend = line.find('"', lonstart + 1)
            lon = float(line[lonstart + 1:lonend])

            pathdict.append((lon, lat))
    
#    myPath = ''
#    limit = 0
#
#    for k, v in pathdict:
#        myPath = myPath + str(k) + "," + str(v) + "|"
#        limit = limit + 1
#
#    pathStr = myPath[:-1

    return pathdict

def distance(pathdict):
    # Haversine formula to calculate distance between GPS coordinates.
    # Written by Wayne Dyck
    
    dist = 0
    
    for item in range(len(pathlist) - 1):
        itemNum = 0
        lat1, lon1 = pathlist[item]
        lat2, lon2 = pathlist[item + 1]
        radius = 3959 # mi

        dlat = math.radians(float(lat2) - float(lat1))
        dlon = math.radians(float(lon2) - float(lon1))
        a = math.sin(dlat / 2) * math.sin(dlat / 2) + math.cos(math.radians(float(lat1))) \
         * math.cos(math.radians(float(lat2))) * math.sin(dlon / 2) * math.sin(dlon / 2)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        dist += radius * c

    return dist

def polyEncoder(pathlist):

    encoder = gpolyencode.GPolyEncoder()
    codedpath = encoder.encode(pathlist)
    points = codedpath['points']

    return points

def largePath(pathlist):

    #    numofrequests = range((numpy.ceil(len(pathlist) / 400.0))).astype('int')
    numofrequests = range(numpy.ceil(len(pathlist) / 400.0).astype('int'))
    ycoord = []
    for i in numofrequests:
        start = (i * 400)
        end = (i + 1) * 400

        partialpathStr = polyEncoder(pathlist[start:end])
        partialycoord = getElevation(partialpathStr)

        ycoord = ycoord + partialycoord

    return ycoord

def elevPlot(y, xDist):

# Uses pylab to plot elevation data.

    # Fill xnums list with len(y) coords evenly spaced
    xnums = []
    incs = xDist / (len(y) - 1)
    for i in range(len(y)):
         xnums.append(i * incs)

    # Plot graph using pylab

    maxelev = (sorted(y)[-1])
    minelev = (sorted(y)[0])
    graphinfo = 'Distance: %.2f\nMax: %i\n Min: %i' % (xDist, maxelev, minelev)
    print "graphinfo: " , graphinfo

    fig, ax = pylab.subplots(1)
    props = dict(boxstyle='round', facecolor='wheat', alpha=0.2)
    ax.text(.99, .99, graphinfo, transform=ax.transAxes, \
            verticalalignment='top', horizontalalignment='right', bbox=props)
    ax.set_xlim(0.0, xDist)
    ax.plot(xnums, y)
    ax.xaxis.set_label_text('Miles')
    ax.yaxis.set_label_text('Feet')
    ax.grid(True)
    ax.set_title('Elevation Profile')
    pylab.show()
   
if __name__ == '__main__':
  
    pathlist = latLonPath(filename) #Parses 'filename' for GPS coordinates
#    pathStr = polyEncoder(pathlist) #Encodes GPS coordinates to Google Polyline Encoding
#    ycoord = getElevation(pathStr) # Google Elevation API to set y coordinates
    ycoord = largePath(pathlist)
    print "ycoord: " , ycoord
    print len(ycoord)
    xdist = distance(pathlist) #Calculates distance to set x coordinates
    elevPlot(ycoord, xdist) #Plots elevation
