import boto3
import os
role_arn = os.environ.get("AWS_ROLE_ARN")
print(role_arn)
sts_client = boto3.client("sts")
response = sts_client.assume_role(RoleArn=role_arn, RoleSessionName="AssumeRoleSession")
print(sts_client)
print(response)