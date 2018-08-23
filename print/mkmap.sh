#!/bin/sh

# kabernet
#perl stitch.pl --lat=58214 --lon=3973764 --zoom=15 --width=3500 --height=3500 --tileBase=https://api.mapbox.com/styles/v1/mikelmaron/cjl34nd460s3z2tn3hz6hlb9s/tiles/256/{z}/{x}/{y}?access_token=pk.eyJ1IjoibWlrZWxtYXJvbiIsImEiOiJjaWZlY25lZGQ2cTJjc2trbmdiZDdjYjllIn0.Wx1n0X7aeCQyDTnK6_mrGw --output=kabernet.png

# eldama

perl stitch.pl --lat=2848 --lon=3977089 --zoom=16 --width=3500 --height=3500 --tileBase=https://api.mapbox.com/styles/v1/mikelmaron/cjl5w24tt08852rlqybihghm2/tiles/256/{z}/{x}/{y}?access_token=pk.eyJ1IjoibWlrZWxtYXJvbiIsImEiOiJjaWZlY25lZGQ2cTJjc2trbmdiZDdjYjllIn0.Wx1n0X7aeCQyDTnK6_mrGw --output=eldama.png
