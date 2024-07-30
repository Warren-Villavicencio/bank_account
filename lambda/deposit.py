import boto3
import os
from decimal import Decimal

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(os.environ['TABLE_NAME'])
ses = boto3.client('ses')

def handler(event, context):
    account_id = event['account_id']
    amount = Decimal(str(event['amount']))

    response = table.update_item(
        Key={'id': account_id},
        UpdateExpression="SET saldo = saldo + :val",
        ExpressionAttributeValues={':val': amount},
        ReturnValues="UPDATED_NEW"
    )

    new_balance = response['Attributes']['saldo']

    # Get account details
    account = table.get_item(Key={'id': account_id})['Item']

    # Send email
    ses.send_email(
        Source='wavillavicencio@utpl.edu.ec',
        Destination={'ToAddresses': [account['correoelectronico']]},
        Message={
            'Subject': {'Data': 'Depósito realizado'},
            'Body': {'Text': {'Data': f"Se ha realizado un depósito de {amount} en su cuenta. Nuevo saldo: {new_balance}"}}
        }
    )

    return {"statusCode": 200, "body": "Depósito realizado y correo enviado"}
