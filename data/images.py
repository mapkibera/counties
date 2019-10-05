#!/usr/bin/python

import os
import string
import geojson
from PIL import Image
from utils import readfile, writefile, url2file

def slug_image(img_url):
  valid_chars = "%s%s" % (string.ascii_letters, string.digits)
  slug = ''.join(c for c in img_url if c in valid_chars)
  return slug

def cache_image(osm_id,img_type, img_url):
  if osm_has_cache(img_url):
    return

  if os.path.exists('cookies.txt'):
    cookies = readfile('cookies.txt').rstrip()

  slug = slug_image(img_url)
  cache_dir = "images/cache/" + osm_id + '/' + slug + '/'
  if not os.path.exists(cache_dir):
    os.makedirs(cache_dir)

  fileName, fileExtension = os.path.splitext(img_url)
  if not fileExtension:
      fileExtension = ".png"
  if not os.path.exists(cache_dir + 'orig' + fileExtension):
    url2file(img_url, cache_dir + 'orig' + fileExtension, cookies)

  if os.path.exists(cache_dir + 'orig' + fileExtension):
    try:
      im = Image.open(cache_dir + 'orig' + fileExtension)
    except IOError:
      print "IMAGE ERROR,can't open image,http://www.osm.org/" + osm_id + "," + img_type + "," + img_url
      #print "orig image error " + cache_dir + 'orig' + fileExtension
      return

    size = 1200, 900
    if not os.path.exists(cache_dir + 'large' + fileExtension):
      try:
        im.thumbnail(size)
        im.save(cache_dir + 'large' + fileExtension)
      except KeyError:
        print "IMAGE ERROR,unknown extension,http://www.osm.org/" + osm_id + "," + img_type + "," + img_url
        #print "unknown extension error " + cache_dir + 'med' + fileExtension
        return

    size = 300, 225
    if not os.path.exists(cache_dir + 'med' + fileExtension):
      try:
        im.thumbnail(size)
        im.save(cache_dir + 'med' + fileExtension)
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
  return img_url.find("baringo_county") == -1
  return img_url.find("https://mapkibera.github.io/counties/data/images/cache/") == 0

def cache_images(counties):
  for county in counties:
    cache_images_county(county)

def cache_images_county(county):
  combined = geojson.loads(readfile("site/" + county + "-projects-matched-merged.geojson"))
  for index, feature in enumerate(combined.features):
    images = []
    large_images = []
    for prop in ["image","image:project"]:
      if prop in feature['properties']:
        cache_image(feature['properties']['osm:id'], prop, feature['properties'][prop])
        #image = get_image_cache(feature['properties']['osm:id'], prop, feature['properties'][prop], 'med')
        #images.append(image)
#        combined.features[index]['properties'][prop] = get_image_cache(feature['properties']['osm:id'], prop, feature['properties'][prop], 'large')
#  dump = geojson.dumps(combined, sort_keys=True, indent=2)
#  return dump

#def osm_cache_change(counties):
