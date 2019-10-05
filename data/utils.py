#!/usr/bin/python

import urllib, urllib2
import logging

def readfile(filename):
  with open(filename, 'r') as f:
    read_data = f.read()
  f.closed
  return read_data

def writefile(file_name, buf):
  myFile = open(file_name, 'w')
  myFile.write(buf)
  myFile.close()

def url2file(url,file_name,cookies=None):
  logging.info("url2file start: " + url)

  opener = urllib2.build_opener()
  if cookies:
    opener.addheaders.append(('Cookie', cookies))
  try:
    rsp = opener.open(url)
  except urllib2.HTTPError, err:
    print str(err.code) + " " + url
    return
  except:
    return
  myFile = open(file_name, 'w')
  myFile.write(rsp.read())
  myFile.close()

  logging.info("url2file end: " + url)


"""
Adapted from https://github.com/brandonxiang/geojson-python-utils
"""
def area(poly):
    """
    calculate the area of polygon
    Keyword arguments:
    poly -- polygon geojson object
    return polygon area
    """
    poly_area = 0
    # TODO: polygon holes at coordinates[1]
    points = poly['coordinates'][0]
    j = len(points) - 1
    count = len(points)

    for i in range(0, count):
        p1_x = points[i][1]
        p1_y = points[i][0]
        p2_x = points[j][1]
        p2_y = points[j][0]

        poly_area += p1_x * p2_y
        poly_area -= p1_y * p2_x
        j = i

    poly_area /= 2
    return poly_area

def centroid(poly):
    """
    get the centroid of polygon
    adapted from http://paulbourke.net/geometry/polyarea/javascript.txt
    Keyword arguments:
    poly -- polygon geojson object
    return polygon centroid
    """
    f_total = 0
    x_total = 0
    y_total = 0
    # TODO: polygon holes at coordinates[1]
    points = poly['coordinates'][0]
    j = len(points) - 1
    count = len(points)

    for i in range(0, count):
        p1_x = points[i][1]
        p1_y = points[i][0]
        p2_x = points[j][1]
        p2_y = points[j][0]

        f_total = p1_x * p2_y - p2_x * p1_y
        x_total += (p1_x + p2_x) * f_total
        y_total += (p1_y + p2_y) * f_total
        j = i

    six_area = area(poly) * 6
    return {'type': 'Point', 'coordinates': [y_total / six_area, x_total / six_area]}

def midpoint(line):
    length = len(line['coordinates'])
    y = (line['coordinates'][0][0] + line['coordinates'][length-1][0]) / 2
    x = (line['coordinates'][0][1] + line['coordinates'][length-1][1]) / 2
    return {'type': 'Point', 'coordinates': [y,x]}
