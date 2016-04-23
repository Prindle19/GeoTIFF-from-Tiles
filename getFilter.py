import sys
import json
from landez import MBTilesBuilder, TilesManager, proj
from osgeo import gdal, osr, ogr
gdal.UseExceptions() 
from osgeo.gdalconst import * 
import csv



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
		print str(totalImages) + " Total Features"
	except IndexError:
		usage()
		return False
	tile_size = 256
	zoomlevels = [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20]
	tms_scheme = False
	srs = osr.SpatialReference()
	srs.SetWellKnownGeogCS("WGS84")
	g = 0
	with open(args[2], 'w') as csvfile:
	    fieldnames = ['z','x','y','v']
	    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
	    writer.writeheader()
	    for feature in layer:
			the_geom = feature.GetGeometryRef()
			the_env = the_geom.GetEnvelope()
			ULLon = the_env[0]
			ULLat = the_env[3]
			LRLon = the_env[1]
			LRLat = the_env[2]
			id = str(g)
			print "Working on %s of %s Features" % (str(g+1),str(totalImages))
			tm = TilesManager(tiles_dir="/tmp",tiles_url="http://{z}/{x}/{y}",cache=False)
			tiles = tm.tileslist(bbox=(ULLon, LRLat, LRLon, ULLat),zoomlevels=zoomlevels)
			for the_tile in tiles:
				print the_tile[0]
				# tilecontent = tm.tile(the_tile)
				projection = proj.GoogleProjection(tile_size, zoomlevels, tms_scheme)
				tileBBOX = projection.tile_bbox(the_tile)
				neLon = tileBBOX[2]
				neLat = tileBBOX[3]
				swLat = tileBBOX[1]
				swLon = tileBBOX[0]	
				bboxWKT = "POLYGON ((%s %s, %s %s, %s %s, %s %s, %s %s))" % (neLon, neLat, neLon, swLat, swLon, swLat, swLon, neLat, neLon, neLat)
				bboxPoly = ogr.CreateGeometryFromWkt(bboxWKT)
				intersection = bboxPoly.Intersection(the_geom)
				if intersection.IsEmpty() == False:
					writer.writerow({'z': the_tile[0], 'x': the_tile[1],'y': the_tile[2], 'v': '1'})
					#print "%s,%s,%s,1" % (the_tile[0],the_tile[1],the_tile[2])
			g+=1


 
def usage():
	print __doc__
 
 
if __name__ == "__main__":
    sys.exit(not main(sys.argv))
