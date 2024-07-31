import boto3

# Inicializar el cliente de DynamoDB
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('cuentabancaria')  # Asegúrate de que este es el nombre correcto de tu tabla

# Datos de los usuarios
users = [
    {'id': 123, 'email': 'warren.greentec@gmail.com'},
    {'id': 234, 'email': 'greentecworld@hotmail.com'}
]

# Actualizar cada usuario
for user in users:
    response = table.update_item(
        Key={'id': user['id']},
        UpdateExpression='SET correoelectronico = :email',
        ExpressionAttributeValues={':email': user['email']},
        ReturnValues="UPDATED_NEW"
    )
    print(f"Usuario {user['id']} actualizado: {response['Attributes']}")

print("Actualización completada.")