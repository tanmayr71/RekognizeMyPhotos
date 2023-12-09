# from variables import *
# import requests


# def lambda_handler(event, context):

#     print("event")
#     print(event)
#     s3_info = event['Records'][0]['s3']
#     bucket_name = s3_info['bucket']['name']
#     key_name = s3_info['object']['key']
#     print(bucket_name)
#     print(key_name)

#     client = boto3.client('rekognition')
#     pass_object = {'S3Object': {'Bucket': bucket_name, 'Name': key_name}}
#     print("pass_object", pass_object)

#     resp = client.detect_labels(Image=pass_object)
#     print("rekognition response")
#     print(resp)
#     timestamp = time.time()

#     labels = []

#     for i in range(len(resp['Labels'])):
#         labels.append(resp['Labels'][i]['Name'])
#     print('<------------Now label list----------------->')
#     print(labels)

#     format = {'objectKey': key_name, 'bucket': bucket_name,
#               'createdTimestamp': timestamp, 'labels': labels}
#     print('I am here')
#     url = ES_URL
#     headers = {"Content-Type": "application/json"}
#     url = "https://search-myphotos1-7aduclkckt6r6ayol6deekjtny.us-east-1.es.amazonaws.com/my-index/_doc"


#     r = requests.post(url, data=json.dumps(format).encode(
#         "utf-8"), headers=headers, auth=(ES_USER, ES_PASS))

    # print(r.text)
    # print('I am here too')
    # return {
    #     'statusCode': 200,
    #     'body': json.dumps('Hello from Lambda!')
    # }
    
    
    
    


# import boto3
# import json
# import requests


# # Replace these with your Elasticsearch configuration

# def update_elasticsearch_index(index_name, document):
#     es.index(index=index_name, body=document)

# def lambda_handler(event, context):
#     # Retrieve information about the uploaded image from the S3 event
#     s3_bucket = event['Records'][0]['s3']['bucket']['name']
#     s3_object_key = event['Records'][0]['s3']['object']['key']
#     # Initialize Rekognition client
#     rekognition = boto3.client('rekognition')
#     # Extract S3 object metadata

#     # Call detectLabels method
#     response = rekognition.detect_labels(
#         Image={
#             'S3Object': {
#                 'Bucket': s3_bucket,
#                 'Name': s3_object_key
#             }
#         },
#         MaxLabels=10,  # Maximum number of labels to return (adjust as needed)
#         MinConfidence=75  # Minimum confidence level for detected labels (adjust as needed)
#     )
    
#     # Process the response - extract and handle labels
#     labels = [label['Name'] for label in response['Labels']]
#     print(labels)
#     # You can further process or store these labels as needed (e.g., in a database or another AWS service)
#     # Initialize S3 client
#     s3 = boto3.client('s3')
#     # Retrieve S3 object metadata
#     try:
#         response = s3.head_object(Bucket=s3_bucket, Key=s3_object_key)
#         print(response)
#         created_timestamp = response['LastModified']
#         created_timestamp = created_timestamp.isoformat()
#         # Check if x-amz-meta-customLabels field exists in metadata
#         # If x-amz-meta-customLabels field exists, create a JSON array

#         if 'customlabels' in response['Metadata']:
#             custom_labels_string = response['Metadata']['customlabels']
#             custom_labels_array = custom_labels_string.split(',')
#             labels.extend(custom_labels_array)
#             # Process or utilize labels_array as needed
#             json_object = {
#             "objectKey": s3_object_key,
#             "bucket": s3_bucket,
#             "createdTimestamp": created_timestamp,
#             "labels": labels
#             }
#         else:
#             print("No custom labels metadata found.")
#             json_object = {
#             "objectKey": s3_object_key,
#             "bucket": s3_bucket,
#             "createdTimestamp": created_timestamp,
#             "labels": labels
#             }
# # print('I am here too')
#         auth = ("Master", "Master@123")
#         index_name = "photoindex"
#         elasticsearch_url = "https://search-myphotos1-7aduclkckt6r6ayol6deekjtny.us-east-1.es.amazonaws.com"
#         url = f"{elasticsearch_url}/{index_name}/_doc/{s3_object_key}"
#         json_object = json.dumps(json_object)
#         print(json_object)
#         response = requests.post(url, data=json_object, auth=auth, headers={"Content-Type": "application/json"})
# # print('I am here too')
#         print(response)
#         print("Response status code:", response.status_code)
#         print("Response headers:", response.headers)
#         print("Response content:", response.content.decode('utf-8'))
#     except Exception as e:
#         print("Error retrieving metadata:", e)
#         return {
#             'statusCode': 500,
#             'body': "Error retrieving metadata."
#         }
# # print('I am here too')
#     return {
#         'statusCode': 200,
#         'body': labels  # Sending labels as the response
#     }

import boto3
import base64
import json
import requests

def lambda_handler(event, context):
    s3 = boto3.client('s3')
    rekognition = boto3.client('rekognition')

    # Retrieve information about the uploaded image from the S3 event
    s3_bucket = event['Records'][0]['s3']['bucket']['name']
    s3_object_key = event['Records'][0]['s3']['object']['key']

    # Get the base64 encoded image object from S3
    response = s3.get_object(Bucket=s3_bucket, Key=s3_object_key)
    base64_encoded_image_content = response['Body'].read()

    # Decode the base64 string
    decoded_image_content = base64.b64decode(base64_encoded_image_content)

    # Call detectLabels method with the decoded image content
    rekognition_response = rekognition.detect_labels(
        Image={'Bytes': decoded_image_content},
        MaxLabels=10,  # Maximum number of labels to return
        MinConfidence=75  # Minimum confidence level for detected labels
    )

    labels = [label['Name'] for label in rekognition_response['Labels']]
    print('Detected labels:', labels)

    # Initialize S3 client for metadata retrieval (if needed)
    response = s3.head_object(Bucket=s3_bucket, Key=s3_object_key)
    print(response)
    created_timestamp = response['LastModified'].isoformat()

    # Check if x-amz-meta-customLabels field exists in metadata
    if 'customlabels' in response['Metadata']:
        custom_labels_string = response['Metadata']['customlabels']
        custom_labels_array = custom_labels_string.split(',')
        labels.extend(custom_labels_array)

    # Prepare JSON object for Elasticsearch
    json_object = {
        "objectKey": s3_object_key,
        "bucket": s3_bucket,
        "createdTimestamp": created_timestamp,
        "labels": labels
    }

    # Post data to Elasticsearch
    auth = ("Master", "Master@123")
    index_name = "photoindex"
    elasticsearch_url = "https://search-myphotos1-7aduclkckt6r6ayol6deekjtny.us-east-1.es.amazonaws.com"
    url = f"{elasticsearch_url}/{index_name}/_doc/{s3_object_key}"
    response = requests.post(url, data=json.dumps(json_object), auth=auth, headers={"Content-Type": "application/json"})

    print(response)
    print("Response status code:", response.status_code)
    print("Response headers:", response.headers)
    print("Response content:", response.content.decode('utf-8'))

    return {
        'statusCode': 200,
        'body': labels  # Sending labels as the response
    }



# from variables import *
# import boto3
# import json
# import requests
# #import time

# # Assuming ES_URL, ES_USER, and ES_PASS are defined as environment variables or imported

# def lambda_handler(event, context):
#     print("event", event)
#     s3_info = event['Records'][0]['s3']
#     bucket_name = s3_info['bucket']['name']
#     key_name = s3_info['object']['key']
#     print(bucket_name, key_name)

#     # Initialize Rekognition client
#     rekognition = boto3.client('rekognition')
#     # Detect labels in the image
#     resp = rekognition.detect_labels(
#         Image={'S3Object': {'Bucket': bucket_name, 'Name': key_name}}
#     )
#     print("rekognition response", resp)
#     labels = [label['Name'] for label in resp['Labels']]
#     print('<-- Detected labels -->', labels)
#     print('hhh')

#     # Initialize S3 client
#     s3 = boto3.client('s3')
#     # Retrieve S3 object metadata
#     metadata_resp = s3.head_object(Bucket=bucket_name, Key=key_name)
#     created_timestamp = time
#     custom_labels = metadata_resp['Metadata'].get('customlabels', '').split(',')
#     labels.extend(custom_labels)  # Combine Rekognition labels with custom labels
    
#     print('I am here')

#     # Prepare data for Elasticsearch
#     document = {
#         'objectKey': key_name,
#         'bucket': bucket_name,
#         'createdTimestamp': created_timestamp,
#         'labels': labels
#     }
#     print('Document to be indexed:', document)
#     print('I am here')

#     # Post data to Elasticsearch
#     es_url = f"{ES_URL}/photoindex/_doc"
#     headers = {"Content-Type": "application/json"}
#     response = requests.post(es_url, data=json.dumps(document), headers=headers, auth=(ES_USER, ES_PASS))

#     print('Elasticsearch response:', response.text)
#     print('I am here')
#     return {
#         'statusCode': 200,
#         'body': json.dumps('Hello from Lambda!')
#     }
