import rasterio
import numpy as np
from shapely.geometry import Point,shape, Polygon, mapping
import json
from rasterio.warp import calculate_default_transform, reproject
from rasterio.enums import Resampling
from rasterio.features import shapes



def raster_to_point(raster_filepath):
    # Open the NDVI raster in UTM CRS
    with rasterio.open(raster_filepath) as src:
    # Get the NDVI band and CRS
        ndvi = src.read(1)
        src_crs = src.crs
    # Get the shape and transform of the raster
        height, width = ndvi.shape
        transform = src.transform
        # Define the destination CRS (WGS 84)
        dst_crs = 'EPSG:4326'
        # Calculate the transformation required to warp the raster
        dst_transform, width, height = calculate_default_transform(src_crs, dst_crs, width, height, *src.bounds)
        # Create empty destination array
        ndvi_wgs84 = np.empty((height, width), dtype=ndvi.dtype)
        # Reproject the NDVI raster to WGS 84
        reproject(ndvi, ndvi_wgs84, src_transform=transform, src_crs=src_crs, dst_transform=dst_transform, dst_crs=dst_crs, dst_nodata = -9999)
        # Create a list to store the point geometries
        print("World")
        points = []
        for i in range(height):
            for j in range(width):
                value = ndvi_wgs84[i, j]
                
                if not np.isnan(value) and value != 0:
                    x_coord, y_coord = dst_transform * (j + 0.5, i + 0.5)
                    #point = Point(x_coord, y_coord, value)
                    point = [str(x_coord),str(y_coord),str(value)]
                    points.append(point)
    
    return points

def raster_to_geojson(raster_filepath,NDVI_threshold):
    # Open the NDVI raster in UTM CRS
    with rasterio.open(raster_filepath) as src:
    # Get the NDVI band and CRS
        ndvi = src.read(1)
        print(ndvi)
        print(ndvi.shape)
        src_crs = src.crs
    # Get the shape and transform of the raster
        height, width = ndvi.shape
        transform = src.transform
        # Define the destination CRS (WGS 84)
        dst_crs = 'EPSG:4326'
        # Calculate the transformation required to warp the raster
        dst_transform, width, height = calculate_default_transform(src_crs, dst_crs, width, height, *src.bounds)
        # Create empty destination array
        ndvi_wgs84 = np.empty((height, width), dtype=ndvi.dtype)
        print(ndvi_wgs84.shape)
        # Reproject the NDVI raster to WGS 84
        reproject(ndvi, ndvi_wgs84, src_transform=transform, src_crs=src_crs, dst_transform=dst_transform, dst_crs=dst_crs,dst_nodata = -9999)
        
        print(ndvi_wgs84)
        

        # Create a list to store the point geometries
        print("World")
        
        
        ndvi_wgs84[ndvi_wgs84 > NDVI_threshold] = 0
        # Check the number of non-zero pixels after masking
        print("Number of non-zero pixels:", np.count_nonzero(ndvi_wgs84))
         # Create polygons for connected groups of pixels with non-zero values
        # Create polygons for connected groups of pixels with non-zero values
        features = []
        for i, (polygon, value) in enumerate(shapes(ndvi_wgs84, mask=ndvi_wgs84 > 0, transform=dst_transform)):
            feature = {
                "type": "Feature",
                "geometry": mapping(shape(polygon)),
                "properties": {"ndvi": value}
            }
            features.append(feature)
        
        print(features)
        # Calculate bbox of all features
        bbox = [float('inf'), float('inf'), float('-inf'), float('-inf')]
        for feature in features:
            bbox_feature = shape(feature['geometry']).bounds
            bbox[0] = min(bbox[0], bbox_feature[0])
            bbox[1] = min(bbox[1], bbox_feature[1])
            bbox[2] = max(bbox[2], bbox_feature[2])
            bbox[3] = max(bbox[3], bbox_feature[3])

        
        '''
        points = []
        for i in range(height):
            for j in range(width):
                print(i,j)
                value = ndvi_wgs84[i, j]
                print(value)
                if value < NDVI_threshold:
                    print(f"Inside {value}")
                    x_coord, y_coord = dst_transform * (j + 0.51, i + 0.51)
                    point = Point(x_coord, y_coord, value)
                    #point = [str(x_coord),str(y_coord),str(value)]
                    points.append(point)
        
    
    # Create a GeoJSON FeatureCollection from the list of Shapely Point objects
    #features = [geojson.Feature(geometry=p, properties={"value": p.z}) for p in points]
    #feature_collection = geojson.FeatureCollection(features)
    
    # Create a GeoJSON FeatureCollection from the list of Shapely Point objects
    features = []
    for point in points:
        feature = {
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [point.x, point.y]
            },
            "properties": {
                "ndvi": point.z
                }
        }
        features.append(feature)

    geojson = {
        "type": "FeatureCollection",
        "features": feature
    }
        '''
     
    geojson = {
        "type": "FeatureCollection",
        "bbox" : bbox,
        "features": features
    }   
        
        
    return geojson
   