GeoTIFF-from-Tiles

Start with Ubuntu 16.04 LTS  


sudo apt-get update

sudo apt-get upgrade

sudo apt-get install unzip python-setuptools gdal-bin python-gdal tmux python-pip

sudo apt-get build-dep python-imaging

sudo easy_install landez

sudo apt-get install python-pip

pip install python-magic

pip install image

mkdir GeoTIFF

cd GeoTIFF

nano getGeoTIFFMBTiles.py

(paste in code from getGeoTIFFMBTiles.py)

wget https://storage.googleapis.com/tile-api-geotiff/AOIs.zip

unzip AOIs.zip

rm AOIs.zip

python getGeoTIFFMBTiles.py AOIs.shp

