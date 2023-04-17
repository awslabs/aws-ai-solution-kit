import boto3


def publish_msg(topic_arn, msg, subject):
    client = boto3.client('sns')
    client.publish(
        TopicArn=topic_arn,
        Message=str(msg),
        Subject=subject
    )
