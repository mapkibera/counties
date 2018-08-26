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
  mbooni = "37.3803,-1.6894,37.4834,-1.614"
  wote = "37.5188,-1.8581,37.6769,-1.7587"

  baringo = "35.521,-0.215,36.495,1.680"
  eldama = "35.6881,-0.0307,35.7553,0.0852"
  kabernet = "35.6147,0.4353,35.7990,0.5916"

  url_base = "http://overpass-api.de/api/interpreter?data=[bbox];node['wb_pb:id'];out%20meta;&bbox="
  url2file(url_base + mbooni,"build/mbooni-projects-osm.xml")
  url2file(url_base + wote,"build/wote-projects-osm.xml")

  url2file(url_base + eldama,"build/eldama-projects-osm.xml")
  url2file(url_base + kabernet,"build/kabernet-projects-osm.xml")

  url_base = "http://overpass-api.de/api/interpreter?data=[bbox];node[~'.'~'.'](newer:'2018-05-01T00:00:00Z');out%20meta;&bbox="
  url2file(url_base + makueni,"build/makueni-poi-osm.xml")
  url2file(url_base + baringo,"build/baringo-poi-osm.xml")


def sync_projects():
  url2file('https://docs.google.com/spreadsheets/u/1/d/1xFKs2JLuIqlsvUnORMwbSx_TOSiedI3ISL2HUPk475k/export?format=csv&id=1xFKs2JLuIqlsvUnORMwbSx_TOSiedI3ISL2HUPk475k&gid=1724788530', 'build/wote-projects-23.csv')
  url2file('https://docs.google.com/spreadsheets/u/1/d/1xFKs2JLuIqlsvUnORMwbSx_TOSiedI3ISL2HUPk475k/export?format=csv&id=1xFKs2JLuIqlsvUnORMwbSx_TOSiedI3ISL2HUPk475k&gid=239806010', 'build/wote-projects-25.csv')
  url2file('https://docs.google.com/spreadsheets/u/1/d/1xFKs2JLuIqlsvUnORMwbSx_TOSiedI3ISL2HUPk475k/export?format=csv&id=1xFKs2JLuIqlsvUnORMwbSx_TOSiedI3ISL2HUPk475k&gid=2140044208', 'build/mbooni.csv')
  url2file('https://docs.google.com/spreadsheets/d/1j5lMG1G0yzk70ujdKK0O9IpjUbgkfB74I5bEjCw6E2s/export?format=csv&id=1j5lMG1G0yzk70ujdKK0O9IpjUbgkfB74I5bEjCw6E2s&gid=502215687', 'build/baringo-projects.csv')

  os.system("tail -n +2 build/wote-projects-25.csv > build/wote-projects-25-clipped.csv")
  os.system("tail -n +2 build/mbooni.csv > build/mbooni-clipped.csv")
  os.system("cat build/wote-projects-23.csv build/wote-projects-25-clipped.csv build/mbooni-clipped.csv > build/makueni-projects.csv")

  os.system("cp build/baringo-projects.csv build/kabernet-projects.csv")
  os.system("cp build/baringo-projects.csv build/eldama-projects.csv")

def convert_geojson():
  os.system("osmtogeojson -e build/makueni-projects-osm.xml > build/makueni-projects-osm.geojson")
  os.system("osmtogeojson -e build/makueni-poi-osm.xml > build/makueni-poi-osm.geojson")
#  os.system("osmtogeojson -e baringo-projects-osm.xml > baringo-projects-osm.geojson")
  os.system("osmtogeojson -e build/kabernet-projects-osm.xml > build/kabernet-projects-osm.geojson")
  os.system("osmtogeojson -e build/eldama-projects-osm.xml > build/eldama-projects-osm.geojson")
  os.system("osmtogeojson -e build/baringo-poi-osm.xml > build/baringo-poi-osm.geojson")

def merge_geojson():
  os.system("geojson-merge kabernet-projects-matched.geojson eldama-projects-matched.geojson > baringo-projects-matched-merged.geojson")

def match_projects(county):
  result = {}
  result['type'] = 'FeatureCollection'
  result['features'] = []

  f = open('build/' + county + '-projects.csv')
  reader = csv.DictReader(f)

  osm = geojson.loads(readfile('build/' + county + '-projects-osm.geojson'))

  for row in reader:
    found_match = False
    for feature in osm.features:
       if feature.properties['tags']['wb_pb:id'] == row['_id'] and found_match == False:
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
      print "WARN: " + county + " no project id match " +  row['_id']

  dump = geojson.dumps(result, sort_keys=True, indent=2)
  writefile(county + '-projects-matched.geojson',dump)

def filter_poi(county):
   result = {}
   result['type'] = 'FeatureCollection'
   result['features'] = []

   osm = geojson.loads(readfile('build/' + county + '-poi-osm.geojson'))
   for feature in osm.features:
       if feature.properties['tags'].get('wb_pb:id', None) == None:
           feature.properties['tags']['osm:id'] = feature.properties['id']
           result['features'].append({ "type": "Feature",  "id": feature.properties["id"], "properties": feature.properties['tags'], "geometry": feature.geometry })

   dump = geojson.dumps(result, sort_keys=True, indent=2)
   writefile(county + '-poi-only.geojson',dump)

def number_projects(county):
   result = {}
   result['type'] = 'FeatureCollection'
   result['features'] = []


   i = 1
   osm = geojson.loads(readfile(county + '-projects-matched.geojson'))
   completed = list(filter(lambda p: p.properties['What_is_the_project_s_apparent_status'] == 'Completed', osm.features))
   in_progress = list(filter(lambda p: p.properties['What_is_the_project_s_apparent_status'] == 'In progress', osm.features))
   not_yet_started = list(filter(lambda p: p.properties['What_is_the_project_s_apparent_status'] == 'Not yet started', osm.features))

   for features in [completed, in_progress, not_yet_started]:
     for feature in sorted(features, key=lambda project: project.properties['Project_Name_or_Title'].strip().lower()):
       feature.properties["iterator"] = i
       result['features'].append(feature)
       i += 1

   dump = geojson.dumps(result, sort_keys=True, indent=2)
   writefile(county + '-projects-numbered.geojson',dump)

def create_index(county):
   projects = geojson.loads(readfile(county + '-projects-numbered.geojson'))
   result = ''
   status = ''
   for feature in projects.features:
       if feature.properties['What_is_the_project_s_apparent_status'] != status:
           status = feature.properties['What_is_the_project_s_apparent_status']
           result = result + status + "\n"

       result = result + str(feature.properties["iterator"]) + ". " + feature.properties['Project_Name_or_Title'] + "\n"

   writefile(county + '-projects-listing.txt', result)

#sync_osm()
#sync_projects()
#convert_geojson()
match_projects('makueni')
##match_projects('baringo')
match_projects('kabernet')
match_projects('eldama')
merge_geojson()
#filter_poi('makueni')
#filter_poi('baringo')
number_projects('kabernet')
number_projects('eldama')
create_index('kabernet')
create_index('eldama')
