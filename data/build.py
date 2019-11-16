#!/usr/bin/python

import os
import logging
from utils import url2file
from images import cache_images, cache_images_county, xml_with_cache_county
from data_manipulation import sync_osm, convert_geojson, merge_geojson, build_centroid, match_projects, filter_poi, number_projects, create_index

logging.basicConfig(level=logging.INFO)

counties = {
  'makueni' : {
    'bbox': '37.37,-1.87695,37.73598,-1.59007',
    'wards' : {
      'mbooni': {
        'bbox': '37.3803,-1.6894,37.4834,-1.614'
      },
      'wote': {
        'bbox': '37.5188,-1.8581,37.6769,-1.75'
      }
    }
  },

  'baringo' : {
    'bbox': '35.521,-0.215,36.495,1.680',
    'wards': {
      'eldama': {
        'bbox': '35.6881,-0.0307,35.7553,0.0852'
      },
      'kabernet': {
        'bbox': '35.6147,0.4353,35.7990,0.5916'
      },
      'marigat': {
        'bbox': '35.776,0.252,36.054,0.616'
      },
      'mogotio': {
        'bbox': '35.6889,-0.0816,35.9805,0.2642'
      }
    }
  },

  'west_pokot': {
    'bbox': '34.9640,1.16104,35.17823,1.42259',
    'wards': {
        'west_pokot_all': {
          'bbox': '34.9640,1.16104,35.17823,1.42259'
        }
    }
  }
}

def sync_projects():
  logging.info("sync_projects start")

  # wote
  url2file('https://docs.google.com/spreadsheets/u/1/d/1xFKs2JLuIqlsvUnORMwbSx_TOSiedI3ISL2HUPk475k/export?format=csv&id=1xFKs2JLuIqlsvUnORMwbSx_TOSiedI3ISL2HUPk475k&gid=1724788530', 'build/wote-projects-23.csv')
  url2file('https://docs.google.com/spreadsheets/u/1/d/1xFKs2JLuIqlsvUnORMwbSx_TOSiedI3ISL2HUPk475k/export?format=csv&id=1xFKs2JLuIqlsvUnORMwbSx_TOSiedI3ISL2HUPk475k&gid=239806010', 'build/wote-projects-25.csv')
  os.system("tail -n +2 build/wote-projects-25.csv > build/wote-projects-25-clipped.csv")
  os.system("cat build/wote-projects-23.csv newline.txt build/wote-projects-25-clipped.csv > build/wote-projects.csv")

  #mbooni
  url2file('https://docs.google.com/spreadsheets/u/1/d/1xFKs2JLuIqlsvUnORMwbSx_TOSiedI3ISL2HUPk475k/export?format=csv&id=1xFKs2JLuIqlsvUnORMwbSx_TOSiedI3ISL2HUPk475k&gid=2140044208', 'build/mbooni.csv')
  os.system("tail -n +2 build/mbooni.csv > build/mbooni-clipped.csv")
  os.system("cp build/mbooni.csv build/mbooni-projects.csv")

  #kabernet, eldama
  url2file('https://docs.google.com/spreadsheets/d/1j5lMG1G0yzk70ujdKK0O9IpjUbgkfB74I5bEjCw6E2s/export?format=csv&id=1j5lMG1G0yzk70ujdKK0O9IpjUbgkfB74I5bEjCw6E2s&gid=502215687', 'build/baringo-projects.csv')
  os.system("grep Kabarnet build/baringo-projects.csv  > build/kabernet-projects.csv")
  os.system("grep -i ravine build/baringo-projects.csv > build/eldama-projects.csv")

  #mogotio, marigat
  url2file('https://docs.google.com/spreadsheets/d/e/2PACX-1vRsaDg2M7vaqMGegAr6pt2-Ud3oCvDxezcVj5VNtGYNlPeR-V_Nd39MFpCsmf9y-ImPTUx0m9yIKsnT/pub?gid=1039418752&single=true&output=csv', 'build/baringo-sept-projects.csv')
  os.system("grep -i mogotio build/baringo-sept-projects.csv > build/mogotio-projects.csv")
  os.system("grep -i marigat build/baringo-sept-projects.csv > build/marigat-projects.csv")

  #west pokot

  url2file('https://docs.google.com/spreadsheets/d/e/2PACX-1vRAfwk0Immx9txJXStyiNRziLY7fsNivskSmkWLzLfjvkDB0L5L-Nm4jLKoSTxLNhs50AwLqSpMbrv-/pub?gid=0&single=true&output=csv', 'build/west_pokot_all-poi.csv')
  url2file('https://docs.google.com/spreadsheets/d/e/2PACX-1vST8fNcolIi00ureHIsuhQxZiLX8rs4F-8Z90pjz-lKYE6c4nnCQ6V86qH8aCMS516e24FfUtA75jXx/pub?gid=1664997779&single=true&output=csv', 'build/west_pokot_all-ways.csv')
  os.system("cat build/west_pokot_all-poi.csv newline.txt > build/west_pokot_all-projects.csv")
  os.system("tail -n +2 build/west_pokot_all-ways.csv >> build/west_pokot_all-projects.csv")
  logging.info("sync_projects complete")

##Get data from OSM
#sync_osm(counties)

##Get project data from Google Sheets
sync_projects()

##Transform OSM data into GeoJSON
convert_geojson(counties)

##Match Project Data to OSM
match_projects(counties)

##Merge Ward Level Matched Data into County Files
merge_geojson(counties)

##Store images locally, and produce modified XML for upload with new image locations
cache_images(counties)

##Filter projects from POI files
filter_poi(counties)

##Order and add numbers to projects
number_projects(counties)

##Create a text index for inclusion in print map
create_index(counties)
