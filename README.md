GeoTIFF-from-Tiles

Start with Ubuntu 14.04 LTS  

sudo apt-get update  
sudo apt-get install unzip python-setuptools gdal-bin python-gdal build-dep python-imaging  
sudo easy_install landez  
mkdir GeoTIFF  
cd GeoTIFF  
nano getGeoTIFF.py  
(paste in code from getGeoTIFF.py)  
wget https://storage.googleapis.com/tile-api-geotiff/AOIs.zip  
unzip AOIs.zip  
rm AOIs.zip  
python getGeoTIFF.py AOIs.shp  
