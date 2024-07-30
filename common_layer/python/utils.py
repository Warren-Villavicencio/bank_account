import boto3
import os

def get_dynamodb_table():
    dynamodb = boto3.resource('dynamodb')
    return dynamodb.Table(os.environ['TABLE_NAME'])

def send_email(to_address, subject, body):
    ses = boto3.client('ses')
    ses.send_email(
        Source='your-verified-email@example.com',
        Destination={'ToAddresses': [to_address]},
        Message={
            'Subject': {'Data': subject},
            'Body': {'Text': {'Data': body}}
        }
    )
