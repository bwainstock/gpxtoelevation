'''
# filename: gpxtoelev.py
# input: gpx file
# Parses gpx XML file to elevation profile using Google Elevation API
'''

from __future__ import print_function
import math
from sys import argv
import urllib
import simplejson
from matplotlib import pyplot as pylab
import numpy
import gpolyencode

ELEVATION_BASE_URL = 'http://maps.google.com/maps/api/elevation/json'
KEY = "AIzaSyBB_e1H1aOubumnTfGDzjcyO3R9CXHK3q8"


def get_elevation(path="", samples="500", sensor="false", **elvtn_args):
    '''
    Google Elevation API call. Takes lat/lon as input, outputs elevation dict
    '''

    encpath = "enc:" + path

    print("len path: ", len(path))

    elvtn_args.update({
        'path': encpath,
        'samples': samples,
        'sensor': sensor
    })

    url = ELEVATION_BASE_URL + '?' + urllib.urlencode(elvtn_args)

    print(len(url))
    print("urllib: ", len(elvtn_args.values()))

    response = simplejson.load(urllib.urlopen(url))

    # Create a dictionary for each results[] object
    elevation_array = []

    for resultset in response['results']:
        elevfeet = resultset['elevation'] * 3.281  # Convert elevation to feet
        elevation_array.append(elevfeet)

    responsefile = open("responsefile", "w")
    responsefile.write(str(response))
    responsefile.close()

    return elevation_array


def lat_lon_path(gpx_filename):
    '''
    Parses gpx file into Google Elevation API formated longitude and latitude
    '''

    trkpt = 'trkpt'

    pathdict = []
    gpx_file = open(gpx_filename)

    for line in gpx_file:
        if trkpt in line:
            latstart = line.find('"')
            latend = line.find('"', latstart + 1)
            lat = float(line[latstart + 1:latend])

            lonstart = line.find('"', latend + 1)
            lonend = line.find('"', lonstart + 1)
            lon = float(line[lonstart + 1:lonend])

            pathdict.append((lon, lat))

    return pathdict


def distance(pathlist):
    '''
    # Haversine formula to calculate distance between GPS coordinates.
    # Written by Wayne Dyck
    '''

    dist = 0

    for item in range(len(pathlist) - 1):
        lat1, lon1 = pathlist[item]
        lat2, lon2 = pathlist[item + 1]
        radius = 3959  # mi

        dlat = math.radians(float(lat2) - float(lat1))
        dlon = math.radians(float(lon2) - float(lon1))
        a = math.sin(dlat / 2) * math.sin(dlat / 2) + math.cos(math.radians(float(lat1))) \
            * math.cos(math.radians(float(lat2))) * math.sin(dlon / 2) * math.sin(dlon / 2)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        dist += radius * c

    return dist


def polyencoder(pathlist):
    '''
    Polyline encoder for Google Maps APIs
    '''

    encoder = gpolyencode.GPolyEncoder()
    codedpath = encoder.encode(pathlist)
    points = codedpath['points']

    return points


def large_path(pathlist):
    '''
    TODO: WRITE DOCSTRING
    '''

    numofrequests = range(numpy.ceil(len(pathlist) / 400.0).astype('int'))
    y_coord = []
    for i in numofrequests:
        start = (i * 400)
        end = (i + 1) * 400

        partial_path_str = polyencoder(pathlist[start:end])
        partialycoord = get_elevation(partial_path_str)

        y_coord = y_coord + partialycoord

    return y_coord


def elev_plot(y, xDist):
    '''
    Plot elevation graph using matplotlib
    '''

    # Fill xnums list with len(y) coords evenly spaced
    xnums = []
    incs = xDist / (len(y) - 1)
    for i in range(len(y)):
        xnums.append(i * incs)

    # Plot graph using pylab

    maxelev = (sorted(y)[-1])
    minelev = (sorted(y)[0])
    graphinfo = 'Distance: %.2f\nMax: %i\n Min: %i' % (xDist, maxelev, minelev)
    print("graphinfo: ", graphinfo)

    fig, ax = pylab.subplots(1)
    props = dict(boxstyle='round', facecolor='wheat', alpha=0.2)
    ax.text(.99, .99, graphinfo, transform=ax.transAxes,
            verticalalignment='top', horizontalalignment='right', bbox=props)
    ax.set_xlim(0.0, xDist)
    ax.plot(xnums, y)
    ax.xaxis.set_label_text('Miles')
    ax.yaxis.set_label_text('Feet')
    ax.grid(True)
    ax.set_title('Elevation Profile')
    pylab.savefig('elevation.png')


def main():
    '''Meat and potatoes'''

    _, filename = argv
    path = lat_lon_path(filename)  # Parses 'filename' for GPS coordinates
#    pathStr = polyencoder(pathlist)   #Encodes GPS coordinates to Google Polyline Encoding
#    ycoord = getElevation(pathStr)  # Google Elevation API to set y coordinates
    ycoord = large_path(path)
    print("ycoord: ", ycoord)
    print(len(ycoord))
    xdist = distance(path)  # Calculates distance to set x coordinates
    elev_plot(ycoord, xdist)  # Plots elevation

if __name__ == '__main__':
    main()
