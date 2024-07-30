import aws_cdk as core
import aws_cdk.assertions as assertions

from bank_account.bank_account_stack import BankAccountStack

# example tests. To run these tests, uncomment this file along with the example
# resource in bank_account/bank_account_stack.py
def test_sqs_queue_created():
    app = core.App()
    stack = BankAccountStack(app, "bank-account")
    template = assertions.Template.from_stack(stack)

#     template.has_resource_properties("AWS::SQS::Queue", {
#         "VisibilityTimeout": 300
#     })
