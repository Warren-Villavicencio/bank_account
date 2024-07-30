import boto3
import os

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(os.environ['TABLE_NAME'])
ses = boto3.client('ses')

def handler(event, context):
    account_id = event['account_id']
    new_pin = event['new_pin']

    response = table.update_item(
        Key={'id': account_id},
        UpdateExpression="SET clavetarjeta = :val",
        ExpressionAttributeValues={':val': new_pin},
        ReturnValues="UPDATED_NEW"
    )

    # Get account details
    account = table.get_item(Key={'id': account_id})['Item']

    # Send email
    ses.send_email(
        Source='your-verified-email@example.com',
        Destination={'ToAddresses': [account['correoelectronico']]},
        Message={
            'Subject': {'Data': 'Cambio de PIN realizado'},
            'Body': {'Text': {'Data': "Se ha cambiado el PIN de su tarjeta de débito. Si no realizó este cambio, por favor contacte con nosotros inmediatamente."}}
        }
    )

    return {"statusCode": 200, "body": "PIN cambiado y correo enviado"}
