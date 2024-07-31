import boto3
import os
import json

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(os.environ['TABLE_NAME'])
ses = boto3.client('ses')

def handler(event, context):
    account_id = event['account_id']
    new_pin = event['new_pin']

    try:
        # Actualizar el PIN
        response = table.update_item(
            Key={'id': account_id},
            UpdateExpression="SET clavetarjeta = :val",
            ExpressionAttributeValues={':val': new_pin},
            ReturnValues="ALL_NEW"
        )

        # Obtener los detalles actualizados de la cuenta
        updated_account = response['Attributes']

        # Verificar si existe el campo de correo electrónico
        if 'correoelectronico' not in updated_account:
            print(f"Advertencia: No se encontró correo electrónico para la cuenta {account_id}")
            return {
                'statusCode': 200,
                'body': json.dumps('PIN cambiado, pero no se pudo enviar correo (correo no encontrado)')
            }

        # Enviar correo electrónico
        ses.send_email(
            Source='wavillavicencio@utpl.edu.ec',
            Destination={'ToAddresses': [updated_account['correoelectronico']]},
            Message={
                'Subject': {'Data': 'Cambio de PIN realizado'},
                'Body': {'Text': {'Data': 'Se ha cambiado el PIN de su tarjeta de débito. Si no realizó este cambio, por favor contacte con nosotros inmediatamente.'}}
            }
        )

        return {
            'statusCode': 200,
            'body': json.dumps('PIN cambiado y correo enviado')
        }
    except Exception as e:
        print(f"Error: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps('Error al procesar la solicitud')
        }