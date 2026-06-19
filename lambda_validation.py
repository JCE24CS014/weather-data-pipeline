import json
import boto3
import urllib.request
from datetime import datetime
import uuid

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('weather0')

API_KEY = "d4e79e06f902500f7df2f55a0a7cb18c"

def lambda_handler(event, context):

    cities = event['cities']

    stored_data = []

    for city in cities:

        try:
            url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric"

            response = urllib.request.urlopen(url)

            data = json.loads(response.read())

            item = {
                'weather_id': str(uuid.uuid4()),
                'city': city,
                'temperature': str(data['main']['temp']),
                'humidity': str(data['main']['humidity']),
                'description': data['weather'][0]['description'],
                'time': str(datetime.now())
            }

            table.put_item(Item=item)

            stored_data.append(item)

        except Exception as e:
            stored_data.append({
                'city': city,
                'error': str(e)
            })

    return {
        'statusCode': 200,
        'body': json.dumps(stored_data)
    }


//weather-data-validator
import boto3
import json

s3 = boto3.client('s3')

BUCKET_NAME = 'weather-data-anagha'

def lambda_handler(event, context):

    for record in event['Records']:

        if record['eventName'] != 'INSERT':
            continue

        item = {}

        for key, value in record['dynamodb']['NewImage'].items():
            item[key] = list(value.values())[0]

        city = item.get('city')
        temp = item.get('temperature')
        humidity = item.get('humidity')

        is_valid = True

        if not city or not temp or not humidity:
            is_valid = False

        if is_valid:
            folder = 'clean-data'
        else:
            folder = 'rejected-data'

        file_name = f"{folder}/{item['weather_id']}.json"

        s3.put_object(
            Bucket=BUCKET_NAME,
            Key=file_name,
            Body=json.dumps(item)
        )

    return {
        'statusCode': 200
    }