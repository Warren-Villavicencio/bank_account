from aws_cdk import (
    Stack,
    aws_dynamodb as dynamodb,
    aws_lambda as _lambda,
    aws_ses as ses,
    aws_iam as iam,
    RemovalPolicy,
)
from constructs import Construct

class BankAccountStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Create DynamoDB table
        table = dynamodb.Table(
            self, "CuentaBancaria",
            table_name="cuentabancaria",
            partition_key=dynamodb.Attribute(name="id", type=dynamodb.AttributeType.NUMBER),
            removal_policy=RemovalPolicy.DESTROY
        )

        # Common Lambda layer for shared code
        common_layer = _lambda.LayerVersion(
            self, "CommonLayer",
            code=_lambda.Code.from_asset("common_layer"),
            compatible_runtimes=[_lambda.Runtime.PYTHON_3_9],
        )

        # Lambda function for depositing money
        deposit_lambda = _lambda.Function(
            self, "DepositLambda",
            runtime=_lambda.Runtime.PYTHON_3_9,
            handler="deposit.handler",
            code=_lambda.Code.from_asset("lambda"),
            environment={
                "TABLE_NAME": table.table_name,
            },
            layers=[common_layer],
        )

        # Lambda function for withdrawing money
        withdraw_lambda = _lambda.Function(
            self, "WithdrawLambda",
            runtime=_lambda.Runtime.PYTHON_3_9,
            handler="withdraw.handler",
            code=_lambda.Code.from_asset("lambda"),
            environment={
                "TABLE_NAME": table.table_name,
            },
            layers=[common_layer],
        )

        # Lambda function for changing debit card PIN
        change_pin_lambda = _lambda.Function(
            self, "ChangePINLambda",
            runtime=_lambda.Runtime.PYTHON_3_9,
            handler="change_pin.handler",
            code=_lambda.Code.from_asset("lambda"),
            environment={
                "TABLE_NAME": table.table_name,
            },
            layers=[common_layer],
        )

        # Grant permissions
        table.grant_read_write_data(deposit_lambda)
        table.grant_read_write_data(withdraw_lambda)
        table.grant_read_write_data(change_pin_lambda)

        # Grant SES permissions to all Lambda functions
        ses_policy = iam.PolicyStatement(
            actions=["ses:SendEmail", "ses:SendRawEmail"],
            resources=["*"],
            effect=iam.Effect.ALLOW,
        )
        deposit_lambda.add_to_role_policy(ses_policy)
        withdraw_lambda.add_to_role_policy(ses_policy)
        change_pin_lambda.add_to_role_policy(ses_policy)