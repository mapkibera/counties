#!/usr/bin/python

import os
import csv
import geojson
import logging
from utils import readfile, writefile, url2file, centroid, midpoint

def sync_osm(counties):
  logging.info("sync_osm start")

  for county in counties:

    url_base = "http://overpass-api.de/api/interpreter?data=[bbox];node[~'.'~'.'](newer:'2018-05-01T00:00:00Z');out%20meta;&bbox="
    url2file(url_base + counties[county]['bbox'],"build/" + county + "-poi-osm.xml")

    for ward in counties[county]['wards']:
      url_base = "http://overpass-api.de/api/interpreter?data=[bbox];node['wb_pb:id'];out%20meta;&bbox="
      url2file(url_base + counties[county]['wards'][ward]['bbox'], "build/" + ward + "-projects-osm.xml")

      url_base = "http://overpass-api.de/api/interpreter?data=[bbox];way['wb_pb:id'];(._;node(w););out%20meta;&bbox="
      url2file(url_base + counties[county]['wards'][ward]['bbox'], "build/" + ward + "-projects-ways-osm.xml")

  logging.info("sync_osm complete")

def convert_geojson(counties):
  logging.info("convert_geojson start")

  for county in counties:
    os.system("osmtogeojson -e build/" + county + "-poi-osm.xml > build/" + county + "-poi-osm.geojson")

    for ward in counties[county]['wards']:
      os.system("osmtogeojson -e build/" + ward + "-projects-osm.xml > build/" + ward + "-projects-nodes-osm.geojson")
      os.system("osmtogeojson -e build/" + ward + "-projects-ways-osm.xml > build/" + ward + "-projects-ways-osm.geojson")
      #build_centroid("build/" + ward + "-projects-ways-osm.geojson", "build/" + ward + "-projects-ways-centroids-osm.geojson")
      ways_only("build/" + ward + "-projects-ways-osm.geojson", "build/" + ward + "-projects-ways-only-osm.geojson")
      #os.system("geojson-merge build/" + ward + "-projects-nodes-osm.geojson build/" + ward + "-projects-ways-centroids-osm.geojson > build/" + ward + "-projects-osm.geojson")
      os.system("geojson-merge build/" + ward + "-projects-nodes-osm.geojson build/" + ward + "-projects-ways-only-osm.geojson > build/" + ward + "-projects-osm.geojson")

  logging.info("convert_geojson complete")

def merge_geojson(counties):
  for county in counties:
    wards = ""
    for ward in counties[county]['wards']:
      wards = wards + 'build/' + ward + "-projects-matched.geojson "
    os.system("geojson-merge " + wards + "> " + "site/"  + county + "-projects-matched-merged.geojson")

def build_centroid(infile, outfile):
  result = {}
  result['type'] = 'FeatureCollection'
  result['features'] = []

  g = geojson.loads(readfile(infile))

  for feature in g.features:
    if feature['geometry']['type'] == "Polygon":
        result['features'].append( { "type": "Feature", "id": feature["id"], "properties": feature.properties, "geometry": centroid(feature.geometry) })
    if feature['geometry']['type'] == "LineString":
        result['features'].append( { "type": "Feature", "id": feature["id"], "properties": feature.properties, "geometry": midpoint(feature.geometry) })

  dump = geojson.dumps(result, sort_keys=True, indent=2)
  writefile(outfile,dump)

def ways_only(infile, outfile):
  result = {}
  result['type'] = 'FeatureCollection'
  result['features'] = []

  g = geojson.loads(readfile(infile))

  for feature in g.features:
    if feature['geometry']['type'] != "Point":
        result['features'].append( feature )

  dump = geojson.dumps(result, sort_keys=True, indent=2)
  writefile(outfile,dump)

def match_projects(counties):
  for county in counties:
    for ward in counties[county]['wards']:
      match_projects_ward(ward)

def match_projects_ward(ward):
  logging.info("match_projects start: " + ward)
  result = {}
  result['type'] = 'FeatureCollection'
  result['features'] = []

  f = open('build/' + ward + '-projects.csv')
  reader = csv.DictReader(f)

  osm = geojson.loads(readfile('build/' + ward + '-projects-osm.geojson'))

  i = 0
  for row in reader:
    i = i+1
    found_match = False
    if '_id' in row:
      id = row['_id']
    elif 'wb_pb:id' in row:
      id = row['wb_pb:id']
    else:
      continue

    if 'Project_Name_or_Title' in row:
       project_name = row['Project_Name_or_Title']
    elif 'Project_Name' in row:
       project_name = row['Project_Name']

    for feature in osm.features:
       print "WARN: " + feature.properties['id']
       if feature.properties['tags']['wb_pb:id'] == id and found_match == False:
         found_match = True

         feature.properties['tags']['Project_Name_or_Title'] = project_name
         if 'Project_Description' in row:
           feature.properties['tags']['Project_Description'] = row['Project_Description']
         if 'Additional_Project_Details' in row:
           feature.properties['tags']['Project_Description'] = row['Additional_Project_Details']
         feature.properties['tags']['Category'] = row['Category']
         feature.properties['tags']['What_is_the_project_s_apparent_status'] = row['What_is_the_project_s_apparent_status']
         feature.properties['tags']['In_your_opinion_is_the_project_quality'] = row['In_your_opinion_is_the_project_quality']
         feature.properties['tags']['Please_add_any_details_about_y'] = row['Please_add_any_details_about_y']
         if 'Project_Name_for_Print' in row and row['Project_Name_for_Print'] != '':
           feature.properties['tags']['Project_Name_for_Print'] = row['Project_Name_for_Print']
         if 'type_of_facility_for print' in row and row['type_of_facility_for print'] != '':
           feature.properties['tags']['type_of_facility_for print'] = row['type_of_facility_for print']
         if 'Budgeted sum' in row:
           feature.properties['tags']['Budgeted sum'] = row['Budgeted sum']

         feature.properties['tags']['osm:id'] = feature.properties['id']

         result['features'].append( { "type": "Feature", "id": feature.properties["id"], "properties": feature.properties['tags'], "geometry": feature.geometry })

    if found_match == False:
      print "WARN: " + str(i) + " " + ward + " no project id match " +  id + " " + project_name

  dump = geojson.dumps(result, sort_keys=True, indent=2)
  writefile('build/' + ward + '-projects-matched.geojson',dump)

  logging.info("match_projects complete: " + ward)

def filter_poi(counties):
  for county in counties:
    filter_poi_county(county)

def filter_poi_county(county):
   result = {}
   result['type'] = 'FeatureCollection'
   result['features'] = []

   osm = geojson.loads(readfile('build/' + county + '-poi-osm.geojson'))
   for feature in osm.features:
       if 'source' in feature.properties['tags']:
         del feature.properties['tags']['source']
       if 'source:date' in feature.properties['tags']:
         del feature.properties['tags']['source:date']

       if feature.properties['tags'].get('wb_pb:id', None) == None and len(feature.properties['tags']) > 0:
           feature.properties['tags']['osm:id'] = feature.properties['id']
           result['features'].append({ "type": "Feature",  "id": feature.properties["id"], "properties": feature.properties['tags'], "geometry": feature.geometry })

   dump = geojson.dumps(result, sort_keys=True, indent=2)
   writefile('site/' + county + '-poi-only.geojson',dump)

def number_projects(counties):
  for county in counties:
    for ward in counties[county]['wards']:
      number_projects_ward(ward)

def number_projects_ward(ward):
   result = {}
   result['type'] = 'FeatureCollection'
   result['features'] = []

   i = 1
   osm = geojson.loads(readfile('build/' + ward + '-projects-matched.geojson'))
   completed = list(filter(lambda p: p.properties['What_is_the_project_s_apparent_status'] in ['Completed', 'completed'], osm.features))
   in_progress = list(filter(lambda p: p.properties['What_is_the_project_s_apparent_status'] in ['In progress','in_progress'], osm.features))
   not_yet_started = list(filter(lambda p: p.properties['What_is_the_project_s_apparent_status'] in ['Not yet started', 'not_yet_starte'], osm.features))

   for features in [completed, in_progress, not_yet_started]:
     for feature in sorted(features, key=lambda project: (project.properties['Project_Name_for_Print'] if 'Project_Name_for_Print' in project.properties else project.properties['Project_Name_or_Title']).strip().lower()):
       feature.properties["iterator"] = i
       result['features'].append(feature)
       i += 1

   dump = geojson.dumps(result, sort_keys=True, indent=2)
   writefile('print/' + ward + '-projects-numbered.geojson',dump)

def create_index(counties):
   for county in counties:
    for ward in counties[county]['wards']:
      create_index_ward(ward)

def create_index_ward(ward):
   projects = geojson.loads(readfile('print/' + ward + '-projects-numbered.geojson'))
   result = ''
   status = ''
   for feature in projects.features:
       if feature.properties['What_is_the_project_s_apparent_status'] != status:
           status = feature.properties['What_is_the_project_s_apparent_status']
           result = result + status + "\n"

       if 'Project_Name_for_Print' in feature.properties:
         name = feature.properties['Project_Name_for_Print']
       else:
         name = feature.properties['Project_Name_or_Title']
       result = result + str(feature.properties["iterator"]) + ". " + name + "\n"

   writefile('print/' + ward + '-projects-listing.txt', result)
