#!/usr/bin/python

import urllib, urllib2
import os
import csv
import geojson

def readfile(filename):
  with open(filename, 'r') as f:
    read_data = f.read()
  f.closed
  return read_data

def writefile(file_name, buf):
  myFile = open(file_name, 'w')
  myFile.write(buf)
  myFile.close()

def url2file(url,file_name):
  req = urllib2.Request(url)
  try:
    rsp = urllib2.urlopen(req)
  except urllib2.HTTPError, err:
    print str(err.code) + " " + url
    return
  myFile = open(file_name, 'w')
  myFile.write(rsp.read())
  myFile.close()

def sync_osm():
  makueni = "37.37,-1.87695,37.73598,-1.59007"
  url_base = "http://overpass-api.de/api/interpreter?data=[bbox];node['wb_pb:id'];out%20meta;&bbox="
  url2file(url_base + makueni,"makueni-projects-osm.xml")

  url_base = "http://overpass-api.de/api/interpreter?data=[bbox];node[~'.'~'.'];out%20meta;&bbox="
  url2file(url_base + makueni,"makueni-poi-osm.xml")

def sync_projects():
  url2file('https://docs.google.com/spreadsheets/u/1/d/1xFKs2JLuIqlsvUnORMwbSx_TOSiedI3ISL2HUPk475k/export?format=csv&id=1xFKs2JLuIqlsvUnORMwbSx_TOSiedI3ISL2HUPk475k&gid=1724788530', 'wote-projects-23.csv')
  url2file('https://docs.google.com/spreadsheets/u/1/d/1xFKs2JLuIqlsvUnORMwbSx_TOSiedI3ISL2HUPk475k/export?format=csv&id=1xFKs2JLuIqlsvUnORMwbSx_TOSiedI3ISL2HUPk475k&gid=239806010', 'wote-projects-25.csv')
  url2file('https://docs.google.com/spreadsheets/u/1/d/1xFKs2JLuIqlsvUnORMwbSx_TOSiedI3ISL2HUPk475k/export?format=csv&id=1xFKs2JLuIqlsvUnORMwbSx_TOSiedI3ISL2HUPk475k&gid=2140044208', 'mbooni.csv')

  os.system("tail -n +2 wote-projects-25.csv > wote-projects-25-clipped.csv")
  os.system("tail -n +2 mbooni.csv > mbooni-clipped.csv")
  os.system("cat wote-projects-23.csv wote-projects-25-clipped.csv mbooni-clipped.csv > makueni-projects.csv")

def convert_geojson():
  os.system("osmtogeojson -e makueni-projects-osm.xml > makueni-projects-osm.geojson")
  os.system("osmtogeojson -e makueni-poi-osm.xml > makueni-poi-osm.geojson")


def match_projects():
  result = {}
  result['type'] = 'FeatureCollection'
  result['features'] = []

  f = open('makueni-projects.csv')
  reader = csv.DictReader(f)

  osm = geojson.loads(readfile('makueni-projects-osm.geojson'))

  for row in reader:
    found_match = False
    for feature in osm.features:
       if feature.properties['tags']['wb_pb:id'] == row['_id']:
         found_match = True
         feature.properties['tags']['Project_Name_or_Title'] = row['Project_Name_or_Title']
         feature.properties['tags']['Project_Description'] = row['Project_Description']
         feature.properties['tags']['Category'] = row['Category']
         feature.properties['tags']['What_is_the_project_s_apparent_status'] = row['What_is_the_project_s_apparent_status']
         feature.properties['tags']['In_your_opinion_is_the_project_quality'] = row['In_your_opinion_is_the_project_quality']
         feature.properties['tags']['Please_add_any_details_about_y'] = row['Please_add_any_details_about_y']

         feature.properties['tags']['osm:id'] = feature.properties['id']

         result['features'].append( { "type": "Feature", "id": feature.properties["id"], "properties": feature.properties['tags'], "geometry": feature.geometry })

    if found_match == False:
      print "WARN: no project id match " +  row['_id']

  dump = geojson.dumps(result, sort_keys=True, indent=2)
  writefile('makueni-projects-matched.geojson',dump)

def filter_poi():
   result = {}
   result['type'] = 'FeatureCollection'
   result['features'] = []

   osm = geojson.loads(readfile('makueni-poi-osm.geojson'))
   for feature in osm.features:
       if feature.properties['tags'].get('wb_pb:id', None) == None:
           feature.properties['tags']['osm:id'] = feature.properties['id']
           result['features'].append({ "type": "Feature",  "id": feature.properties["id"], "properties": feature.properties['tags'], "geometry": feature.geometry })

   dump = geojson.dumps(result, sort_keys=True, indent=2)
   writefile('makueni-poi-only.geojson',dump)

sync_osm()
sync_projects()
convert_geojson()
match_projects()
filter_poi()
