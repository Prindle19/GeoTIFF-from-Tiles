import sys
import json
from landez import MBTilesBuilder, TilesManager, proj
from osgeo import gdal, osr, ogr
gdal.UseExceptions() 
from osgeo.gdalconst import * 
import os
import magic
import time
from PIL import Image
import StringIO


def CalcGeoTransform(tileBBOX, fileName):
	NELong = tileBBOX[2]
	NELat = tileBBOX[3]
	SWLat = tileBBOX[1]
	SWLong = tileBBOX[0]
	NWLong = SWLong
	NWLat = NELat
	ppx = (NELong - SWLong) / 256
	ppy = (SWLat - NELat) / 256
	return (NWLong, ppx, 0.00000, NWLat, 0.00000, ppy)

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
		the_env = the_geom.GetEnvelope()
		ULLon = the_env[0]
		ULLat = the_env[3]
		LRLon = the_env[1]
		LRLat = the_env[2]
		id = str(g)
		print  id + " " + str(g+1) + " of " + str(totalImages)
		tm = TilesManager(tiles_dir="/tmp",tiles_url="https://tile-live.appspot.com/getTile/?z={z}&x={x}&y={y}&layer=derivative&redirect=false")
		tiles = tm.tileslist(bbox=(ULLon, LRLat, LRLon, ULLat),zoomlevels=zoomlevels)
		x = 0
		y = 0
		z = 0
		for the_tile in tiles:
			tilecontent = tm.tile(the_tile)
			fileType = magic.from_buffer(tilecontent, mime=True)
			fileRoot = id + "-" + str(x)
			projection = proj.GoogleProjection(tile_size, zoomlevels, tms_scheme)
			tileBBOX = projection.tile_bbox(the_tile)			
			im = Image.open(StringIO.StringIO(tilecontent))
			fileName = fileRoot + ".tiff"
			print fileName + str(tileBBOX)
			im.save(fileName)
			im.close()
			try:
				ds = gdal.Open(fileName, GA_Update)
				gt = CalcGeoTransform(tileBBOX, fileName)
				ds.SetGeoTransform(gt)
				ds.SetProjection(srs.ExportToWkt())
				if ds.RasterCount == 3:
					drv = gdal.GetDriverByName('VRT')
					newDS = drv.CreateCopy(fileRoot + '.vrt', ds, 0)
					newDS.AddBand(gdal.GDT_Byte)
					newDS.GetRasterBand(4).SetColorInterpretation(GCI_AlphaBand)
					drv2 = gdal.GetDriverByName('GTiff')
					outDS = drv2.CreateCopy(fileRoot + '-4.tiff', newDS, 0)
					outDS.GetRasterBand(4).Fill(255)
					newDS = None
					outDS = None
					os.system('rm ' + fileName)
					os.system('rm ' + fileRoot + '.vrt')
					os.system('mv ' + fileRoot + '-4.tiff ' + fileName)
				ds = None

				# warpString = 'gdalwarp ' + fileName + ' clipped-' + fileRoot + '.tiff' + ' -cutline AOIs.shp -cwhere "id = \'' + str(the_ID) + '\'"'
				# print warpString
				os.system('gdalwarp ' + fileName + ' clipped-' + fileRoot + '.tiff' + ' -cutline AOIs.shp -cwhere "id = \'' + str(the_ID) + '\'"')
				os.system('rm ' + fileName)
				os.system('mv clipped-' + fileRoot + '.tiff ' + fileName)
			except RuntimeError as ex:
				raise IOError(ex)
				print "Weird one"
			x += 1
			y += 1
			if y == 1000:
				mosaicName = "mosaic" + str(z) + ".vrt"	
				if z == 0:		
					os.system('gdalbuildvrt ' + mosaicName + ' *.tiff')
				else:
					mosaicList = id + '-' + str(z) +'[0-9][0-9][0-9].tiff'
					os.system('gdalbuildvrt ' + mosaicName + ' ' + mosaicList)
				y = 0
				z += 1
		if z > 0:
			os.system('gdalbuildvrt rest.vrt ' + id + '-' + str(z) +'[0-9][0-9][0-9].tiff')
			os.system('gdalbuildvrt mosaic.vrt *.vrt')
                        os.system('gdal_translate -of GTiff -projwin ' + str(ULLon) + " " + str(ULLat) + " " + str(LRLon) + " " + str(LRLat) + ' mosaic.vrt ' + id + ".tiff")
                        os.system('rm *.aux.xml && rm *.png && rm *.vrt')
			z = 0
		else:
			os.system('gdalbuildvrt mosaic.vrt ' + id + '-*.tiff')
			os.system('gdal_translate -of GTiff -projwin ' + str(ULLon) + " " + str(ULLat) + " " + str(LRLon) + " " + str(LRLat) + ' mosaic.vrt ' + id + ".tiff")
			os.system('rm ' + id +'-*.tiff && rm *.vrt')
			
		g += 1
	os.system('ls *.tiff > filelist')
	os.system('tar -zcvf GoogleImages.tar.gz $(cat filelist)')
 
def usage():
	print __doc__
 
 
if __name__ == "__main__":
    sys.exit(not main(sys.argv))
