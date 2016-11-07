import sys
import json
import landez
from landez import MBTilesBuilder, TilesManager, proj
from osgeo import gdal, osr, ogr
gdal.UseExceptions() 
from osgeo.gdalconst import * 
import os
import logging
logging.basicConfig(level=logging.DEBUG)


landez.DOWNLOAD_RETRIES = 40


def main(args):
	try:
		shapefile = args[1]
		driver = ogr.GetDriverByName("ESRI Shapefile")
		dataSource = driver.Open(shapefile, 0)		
		layer = dataSource.GetLayer()
		totalImages = layer.GetFeatureCount()
		print str(totalImages) + " Total Images"
	except IndexError:
		usage()
		return False

	tile_size = 256
	zoomlevels = [20]
	tms_scheme = False
	srs = osr.SpatialReference()
	srs.SetWellKnownGeogCS("WGS84")
	g = 0
	for feature in layer:
		the_ID = feature.GetField("id")
		the_name = feature.GetField("Name")
		the_geom = feature.GetGeometryRef()
		bufferDistance = .0006
		the_geom = the_geom.Buffer(bufferDistance)
		the_env = the_geom.GetEnvelope()
		ULLon = the_env[0]
		ULLat = the_env[3]
		LRLon = the_env[1]
		LRLat = the_env[2]
		id = str(g)
		print  id + " " + str(g+1) + " of " + str(totalImages)
		mbTileName = id + ".mbtiles"
		tempTiffName = id + ".tiff"
		mb = MBTilesBuilder(tiles_url="https://tile-live.appspot.com/getTile/?z={z}&x={x}&y={y}&layer=derivative&redirect=false", filepath=mbTileName,ignore_errors="true")
		mb.add_coverage(bbox=(ULLon, LRLat, LRLon, ULLat),zoomlevels=[20])
		mb.run()
		os.system('gdal_translate ' + mbTileName + ' ' + tempTiffName)
		os.system('gdalwarp  ' + tempTiffName + ' clipped-' + id + '.tiff' + ' -cutline AOIs.shp -crop_to_cutline -dstalpha -cwhere "id = \'' + str(the_ID) + '\'"')
		os.system('rm ' + tempTiffName)
		os.system('mv clipped-' + id + '.tiff ' + tempTiffName)
		os.system('gsutil cp ' + id + '.tiff gs://tile-to-geotiff/iupui/mbtiles/')
		os.system('gsutil cp ' + mbTileName + ' gs://tile-to-geotiff/iupui/mbtiles/')
		g += 1

 
def usage():
	print __doc__
 
 
if __name__ == "__main__":
    sys.exit(not main(sys.argv))
