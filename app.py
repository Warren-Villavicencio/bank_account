import aws_cdk as cdk
from bank_account.bank_account_stack import BankAccountStack

app = cdk.App()
BankAccountStack(app, "BankAccountStack")
app.synth()
