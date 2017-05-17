import sys
import boto3
from botocore.exceptions import ClientError
import json
import requests


def lambda_handler(event, context):
    print(event)
    print(f'Request type is {event["RequestType"]}')
    if event['RequestType'] == 'Delete':
        sendResponse(event, context, 'SUCCESS', {})
        return 0

    ami_name = event['ResourceProperties']['Name']  # Get AMI Name
    ami_owner = event['ResourceProperties']['Owner']  # Get AMI Owner
    ami_region = event['ResourceProperties']['Region']  # Get AWS Region
    virtualization_type = event['ResourceProperties'][
        'VirtualizationType']  # Get AMI VirtualizationType
    root_device_type = event['ResourceProperties'][
        'RootDeviceType']  # Get AMI RootDeviceType

    try:
        client = boto3.client('ec2', region_name=ami_region)
        response = client.describe_images(
            Owners=[ami_owner],
            Filters=[
                {'Name': 'name', 'Values': [ami_name]},
                {'Name': 'virtualization-type',
                    'Values': [virtualization_type]},
                {'Name': 'root-device-type', 'Values': [root_device_type]}
            ]
        )

        # Collect Images Found
        images = response['Images']

        # If no images found, send a failed response.
        if len(images) == 0:
            print(f'No images found')
            sendResponse(event, context, 'FAILED', {
                         'Error': 'No Images Found'})

        # Sort Images by name
        sorted_images = sorted(images, key=lambda k: k['Name'])

        # Since the Image names include a timestamp, the most recent AMI will
        # be the last element
        latest_image = sorted_images[-1]

        print(f'Latest image is {latest_image["Name"]} and ID {latest_image["ImageId"]}')
        responseData = {'ImageId': latest_image['ImageId']}
        sendResponse(event, context, 'SUCCESS', responseData)
    except ClientError as e:
        print(f'Recieved client error {e}')
        responseData = {'Error': e}
        sendResponse(event, context, 'FAILED', responseData)


def sendResponse(event, context, responseStatus, responseData):
    responseBody = {
        'Status': responseStatus,
        'Reason': f'See the details in CloudWatch Log Stream: {context.log_stream_name}',
        'PhysicalResourceId': context.log_stream_name,
        'StackId': event['StackId'],
        'RequestId': event['RequestId'],
        'LogicalResourceId': event['LogicalResourceId'],
        'Data': responseData}

    print(f'Response Body: {json.dumps(responseBody)}')

    try:
        req = requests.put(event['ResponseURL'], data=json.dumps(responseBody))
        if req.status_code != 200:
            print(req.text)
            raise Exception(f'Recieved non 200 response while sending response to {event["ResponseURL"]}')
        return
    except requests.exceptions.RequestException as e:
        print(e)
        raise

if __name__ == '__main__':
    lambda_handler('event', 'handler')
