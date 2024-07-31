import boto3
import os
import json
from botocore.exceptions import ClientError

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(os.environ['TABLE_NAME'])
ses = boto3.client('ses')

def handler(event, context):
    account_id = event.get('account_id')
    new_pin = event.get('new_pin')

    if not account_id or not new_pin:
        return {
            'statusCode': 400,
            'body': json.dumps('Missing account_id or new_pin')
        }

    try:
        # Get the current account details
        response = table.get_item(Key={'id': account_id})
        
        if 'Item' not in response:
            return {
                'statusCode': 404,
                'body': json.dumps(f'Account with id {account_id} not found')
            }

        account = response['Item']
        
        # Update the PIN, initialize if not exists
        try:
            table.update_item(
                Key={'id': account_id},
                UpdateExpression="SET clavetarjeta = :val",
                ExpressionAttributeValues={':val': new_pin}
            )
        except ClientError as e:
            if e.response['Error']['Code'] == 'ValidationException':
                # If clavetarjeta doesn't exist, create it
                table.update_item(
                    Key={'id': account_id},
                    UpdateExpression="SET clavetarjeta = :val",
                    ExpressionAttributeValues={':val': new_pin}
                )
            else:
                raise

        # Check if email exists and send email
        if 'correoelectronico' in account:
            ses.send_email(
                Source='wavillavicencio@utpl.edu.ec',
                Destination={'ToAddresses': [account['correoelectronico']]},
                Message={
                    'Subject': {'Data': 'Cambio de PIN realizado'},
                    'Body': {'Text': {'Data': 'Se ha cambiado el PIN de su tarjeta de débito. Si no realizó este cambio, por favor contacte con nosotros inmediatamente.'}}
                }
            )
            return {
                'statusCode': 200,
                'body': json.dumps('PIN cambiado y correo enviado')
            }
        else:
            print(f"Advertencia: No se encontró correo electrónico para la cuenta {account_id}")
            return {
                'statusCode': 200,
                'body': json.dumps('PIN cambiado, pero no se pudo enviar correo (correo no encontrado)')
            }

    except Exception as e:
        print(f"Error: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps('Error al procesar la solicitud')
        }