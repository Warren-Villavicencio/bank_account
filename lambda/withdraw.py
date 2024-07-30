import boto3
import os
from decimal import Decimal

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(os.environ['TABLE_NAME'])
ses = boto3.client('ses')

def handler(event, context):
    account_id = event['account_id']
    amount = Decimal(str(event['amount']))

    # Check if sufficient balance
    account = table.get_item(Key={'id': account_id})['Item']
    if account['saldo'] < amount:
        return {"statusCode": 400, "body": "Saldo insuficiente"}

    response = table.update_item(
        Key={'id': account_id},
        UpdateExpression="SET saldo = saldo - :val",
        ExpressionAttributeValues={':val': amount},
        ReturnValues="UPDATED_NEW"
    )

    new_balance = response['Attributes']['saldo']

    # Send email
    ses.send_email(
        Source='your-verified-email@example.com',
        Destination={'ToAddresses': [account['correoelectronico']]},
        Message={
            'Subject': {'Data': 'Retiro realizado'},
            'Body': {'Text': {'Data': f"Se ha realizado un retiro de {amount} de su cuenta. Nuevo saldo: {new_balance}"}}
        }
    )

    return {"statusCode": 200, "body": "Retiro realizado y correo enviado"}
