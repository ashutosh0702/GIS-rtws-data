import boto3
import os
import json
from datetime import timedelta, datetime
from geospatial import raster_to_point, raster_to_geojson
from ndvi import threshold

s3 = boto3.client("s3")
res = boto3.resource("s3")
bucket_name = "boundary-plot"
bucket_name_raster = "sentinel-2-cogs-rnil"
REALTIME_PATH = "/realtime"
GEOJSON_PATH = "/geojson"

def lambda_handler(event, context):
    print(event)
    if event['resource'] == REALTIME_PATH:
        try:
            farmID = event['queryStringParameters']['farmID']
            farmName = event['queryStringParameters']['farmName']
            date = event['queryStringParameters']['date']
        except:
            return {
                "statusCode": 400,
                "body": json.dumps("Please provide/check query string parameters")
            }
        try:
            date_obj = datetime.strptime(date, '%Y-%m-%d').date()
        except ValueError:
            return {
                "statusCode": 400,
                "body": json.dumps("Please provide/check query string parameters")
            }
        start_date = date_obj - timedelta(days=5)
        end_date = date_obj + timedelta(days=1)
        print(start_date, end_date)
        objects = s3.list_objects_v2(Bucket=bucket_name_raster, Prefix=f"{farmID}_{farmName}")['Contents']
        matching_objects = [obj for obj in objects if obj['Key'].endswith('NDVI.tif') and start_date <= datetime.strptime(obj['Key'].split('/')[1].split('_')[0], '%Y-%m-%d').date() <= end_date]
        print(objects)
        print(matching_objects)
        if not matching_objects:
            return {
                "statusCode": 400,
                "body": json.dumps("No data found")
            }
        object_key = matching_objects[0]['Key']
        object_url = s3.generate_presigned_url('get_object', Params={'Bucket': bucket_name, 'Key': object_key})
        object_path = f"/tmp/{farmID}.tif"
        s3.download_file(bucket_name_raster, object_key, object_path)
        print(object_url)
        result = {}
        result['ndvi'] = raster_to_point(object_path)
        responseObject = {
            "statusCode": 200,
            "headers": {"Content-Type": 'application/json'},
            "body": json.dumps(result)
        }
    elif event['resource'] == GEOJSON_PATH:
        
        
        
        print(event)
        
        try:
            farmID  = event['queryStringParameters']['farmID']
            farmName = event['queryStringParameters']['farmName']
            cropName = event['queryStringParameters']['cropName'].lower()
            week = event['queryStringParameters']['week'].lower()
            date = event['queryStringParameters']['date']
            
        except:
            return {
                "statusCode" : 400,
                "body" : json.dumps("Please provide/check query string parameters")
            }
        

        try:
            date_obj = datetime.strptime(date, '%Y-%m-%d').date()
        except ValueError:
            return {
                "statusCode" : 400,
                "body" : json.dumps("Please provide/check query string parameters")
            }
            
            
        start_date = date_obj - timedelta(days=10)
        end_date = date_obj + timedelta(days=1)
        print(start_date,end_date)
        
        objects = s3.list_objects_v2(Bucket=bucket_name_raster, Prefix=f"{farmID}_{farmName}")['Contents']
        print(objects)
        matching_objects = [obj for obj in objects if obj['Key'].endswith('NDVI.tif') and obj['Key'].startswith(f'{farmID}_') and start_date <= datetime.strptime(obj['Key'].split('/')[1].split('_')[0], '%Y-%m-%d').date() <= end_date]
        
        print(objects)
        print(matching_objects)
        
        if not matching_objects:
            return {
                "statusCode" : 400,
                "body" : json.dumps("No data found")
            }
        
        
        object_key = matching_objects[0]['Key']
        object_url = s3.generate_presigned_url('get_object', Params={'Bucket': bucket_name, 'Key': object_key})
        object_path = f"/tmp/{farmID}.tif"
        
        s3.download_file(bucket_name_raster, object_key, object_path)
        
        print(object_url)
        
        ndvi_threshold = threshold[cropName][week]
        print(ndvi_threshold)

        result = raster_to_geojson(object_path, ndvi_threshold)
    
        #Construct http response object
        responseObject = {}
        responseObject['statusCode'] = 200
        responseObject['headers'] = {}
        responseObject['headers']['Content-Type'] = 'application/json'
        responseObject['body'] = json.dumps(result)
        
       
    return responseObject
