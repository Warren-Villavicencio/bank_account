import boto3
import os
import json
from decimal import Decimal
from botocore.exceptions import ClientError

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(os.environ['TABLE_NAME'])
ses = boto3.client('ses')

def handler(event, context):
    account_id = event.get('account_id')
    amount = event.get('amount')

    if not account_id or amount is None:
        return {
            'statusCode': 400,
            'body': json.dumps('Missing account_id or amount')
        }

    try:
        amount = Decimal(str(amount))
    except:
        return {
            'statusCode': 400,
            'body': json.dumps('Invalid amount')
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
        
        # Update the balance, initialize if not exists
        try:
            response = table.update_item(
                Key={'id': account_id},
                UpdateExpression="SET saldo = if_not_exists(saldo, :zero) + :val",
                ExpressionAttributeValues={':val': amount, ':zero': Decimal('0')},
                ReturnValues="UPDATED_NEW"
            )
        except ClientError as e:
            if e.response['Error']['Code'] == 'ValidationException':
                # If saldo doesn't exist, create it
                response = table.update_item(
                    Key={'id': account_id},
                    UpdateExpression="SET saldo = :val",
                    ExpressionAttributeValues={':val': amount},
                    ReturnValues="UPDATED_NEW"
                )
            else:
                raise

        new_balance = response['Attributes']['saldo']

        # Check if email exists and send email
        if 'correoelectronico' in account:
            ses.send_email(
                Source='wavillavicencio@utpl.edu.ec',
                Destination={'ToAddresses': [account['correoelectronico']]},
                Message={
                    'Subject': {'Data': 'Depósito realizado'},
                    'Body': {'Text': {'Data': f"Se ha realizado un depósito de {amount} en su cuenta. Nuevo saldo: {new_balance}"}}
                }
            )
            return {
                'statusCode': 200,
                'body': json.dumps('Depósito realizado y correo enviado')
            }
        else:
            print(f"Advertencia: No se encontró correo electrónico para la cuenta {account_id}")
            return {
                'statusCode': 200,
                'body': json.dumps('Depósito realizado, pero no se pudo enviar correo (correo no encontrado)')
            }

    except Exception as e:
        print(f"Error: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps('Error al procesar la solicitud')
        }