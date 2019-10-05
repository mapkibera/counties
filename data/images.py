#!/usr/bin/python

import os
import string
import geojson
from PIL import Image
from utils import readfile, writefile, url2file

import xml.etree.ElementTree as ET


def slug_image(img_url):
  valid_chars = "%s%s" % (string.ascii_letters, string.digits)
  slug = ''.join(c for c in img_url if c in valid_chars)
  return slug

def get_cache_dir(osm_id,img_url):
  slug = slug_image(img_url)
  return "images/cache/" + osm_id + '/' + slug + '/'

def get_file_path(cache_dir, img_url, size):
  fileName, fileExtension = os.path.splitext(img_url)

  if not fileExtension:
    fileExtension = ".png"

  return cache_dir + size + fileExtension

def cache_image(osm_id,img_type, img_url):
  if osm_has_cache(img_url):
    return

  if os.path.exists('cookies.txt'):
    cookies = readfile('cookies.txt').rstrip()

  cache_dir = get_cache_dir(osm_id, img_url)
  if not os.path.exists(cache_dir):
    os.makedirs(cache_dir)

  file_path = get_file_path(cache_dir, img_url, 'orig')

  if not os.path.exists(file_path):
    url2file(img_url, file_path, cookies)

  if os.path.exists(file_path):
    try:
      im = Image.open(file_path)
    except IOError:
      print "IMAGE ERROR,can't open image,http://www.osm.org/" + osm_id + "," + img_type + "," + img_url
      #print "orig image error " + cache_dir + 'orig' + fileExtension
      return

    size = 1200, 900
    if not os.path.exists(get_file_path(cache_dir, img_url, 'large')):
      try:
        im.thumbnail(size)
        im.save(get_file_path(cache_dir, img_url, 'large'))
      except KeyError:
        print "IMAGE ERROR,unknown extension,http://www.osm.org/" + osm_id + "," + img_type + "," + img_url
        #print "unknown extension error " + cache_dir + 'med' + fileExtension
        return

    size = 300, 225
    if not os.path.exists(get_file_path(cache_dir, img_url, 'med')):
      try:
        im.thumbnail(size)
        im.save(get_file_path(cache_dir, img_url, 'med'))
      except KeyError:
        print "IMAGE ERROR,unknown extension,http://www.osm.org/" + osm_id + "," + img_type + "," + img_url
        #print "unknown extension error " + cache_dir + 'med' + fileExtension
        return

  else:
    print "IMAGE ERROR,orig missing,http://www.osm.org/" + osm_id + "," + img_type + "," + img_url
    #print "orig image missing " + cache_dir + 'orig' + fileExtension

def get_image_cache(osm_id, img_type, img_url, cache_size):
  slug = slug_image(img_url)
  cache_path = "https://mapkibera.github.io/counties/data/images/cache/" + osm_id + '/' + slug + '/'
  fileName, fileExtension = os.path.splitext(img_url)
  return cache_path + cache_size + fileExtension

def osm_has_cache(img_url):
  return img_url.find("https://mapkibera.github.io/counties/data/images/cache/") == 0

def cache_images(counties):
  for county in counties:
    cache_images_county(county)
    for ward in counties[county]['wards']:
      xml_with_cache_county(ward)

def cache_images_county(county):
  combined = geojson.loads(readfile("site/" + county + "-projects-matched-merged.geojson"))
  for index, feature in enumerate(combined.features):
    images = []
    large_images = []
    for prop in ["image","image:project"]:
      if prop in feature['properties']:
        cache_image(feature['properties']['osm:id'], prop, feature['properties'][prop])

def xml_with_cache_county(ward):
  tree = ET.parse('build/' + ward + '-projects-osm.xml')
  nodes = tree.findall('node')
  for node in nodes:
    for prop in ["image","image:project"]:
      tag = node.find('.//tag[@k="' + prop + '"]')
      if tag != None:
        cache_dir = get_cache_dir(node.attrib['id'], tag.attrib['v'])
        file_path = get_file_path(cache_dir, tag.attrib['v'], 'orig')
        if os.path.exists(file_path):
          tag.attrib['v'] = "https://mapkibera.github.io/counties/data/" + file_path
          node.attrib['action'] = 'modify'

  writefile('build/' + ward + '-projects-osm-images.xml',ET.tostring(tree.getroot()))

  tree = ET.parse('build/' + ward + '-projects-ways-osm.xml')
  ways = tree.findall('way')
  for way in ways:
    for prop in ["image","image:project"]:
      tag = way.find('.//tag[@k="' + prop + '"]')
      if tag != None:
        cache_dir = get_cache_dir(way.attrib['id'], tag.attrib['v'])
        file_path = get_file_path(cache_dir, tag.attrib['v'], 'orig')
        if os.path.exists(file_path):
          tag.attrib['v'] = "https://mapkibera.github.io/counties/data/" + file_path
          way.attrib['action'] = 'modify'

  writefile('build/' + ward + '-projects-ways-osm-images.xml',ET.tostring(tree.getroot()))
