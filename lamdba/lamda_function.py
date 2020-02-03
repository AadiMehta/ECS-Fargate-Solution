import boto3
import logging
import json
from botocore.exceptions import ClientError


sqs_client = boto3.client('sqs')
sqs_queue_url = "SQS Queue Url"  # e.g "https://sqs.us-west-2.amazonaws.com/<account-Id>/<queue-name>"

ecs_client = boto3.client('ecs')


def send_sqs_message(msg_body):
    """
    :param sqs_queue_url: String URL of existing SQS queue
    :param msg_body: String message body
    :return: Dictionary containing information about the sent message. If
        error, returns None.
    """
    # Send the SQS message
    try:
        msg = sqs_client.send_message(QueueUrl=sqs_queue_url, MessageBody=str(msg_body))
    except ClientError as e:
        logging.error(e)
        return None
    return msg

def run_ecs_task():
    """
    Run ECS task
    """
    try:
        networkConfiguration=dict({
         'awsvpcConfiguration': {
             'subnets': [
                 'subnet-0c71b1af2b69a626a',
             ],
             'securityGroups': [
                 'sg-0aff681b2b7ad6206',
             ],
             'assignPublicIp': 'ENABLED'
         }
        })
        ecs_client.run_task(launchType='FARGATE', networkConfiguration=networkConfiguration, cluster='ClusterName', taskDefinition='TaskName', count=1)
    except Exception as e:
        logging.error(e)
        print(str(e))

def lambda_handler(event, context):
    """
	Sample event looks like following:

	{
    	"message": {
    		"data": "test-example.svs",
    		"retry": False,
    		"other_data": "any other data"
    	}
    }
	"""
    data = json.loads(event["body"])
    if not data.get("retry", False):
        print("New conversion request")
        send_sqs_message(json.dumps(data))
        run_ecs_task()
    else:
        print("Retrying logic")
        run_ecs_task()
    print("Done!")
    return {
        "statusCode": 200,
        "headers": {
            "x-image-header" : "My Precious"
        },
        "body": str("{\"message\": \"success\"}")
    }
