"""
ssh -i "/Users/hanshanli/Desktop/Columbia/COMS6156/credentials/private.pem" ec2-user@ec2-18-219-149-124.us-east-2.compute.amazonaws.com
"""
import boto3

REGION = 'us-east-2'
ACCESS_ID = 'AKIA4UZGX6D4ZACYUAHD'
ACCESS_KEY = 'ZY0gKoxW/sHu83fH+w2vzLWTgReh71bpY8Eh2W69'
sns = boto3.resource(
    "sns",
    region_name=REGION,
    aws_access_key_id=ACCESS_ID,
    aws_secret_access_key=ACCESS_KEY)

def create_topic(name):
    """
    Creates a notification topic.

    :param name: The name of the topic to create.
    :return: The newly created topic.
    """
    topic_arn = sns.create_topic(Name=name)
    print("topic created")
    return topic_arn

def delete_topic(topic):
    """
    Deletes a topic. All subscriptions to the topic are also deleted.
    """
    topic.delete()
    print("topic deleted")

def list_topics():
    """
    Lists topics for the current account.

    :return: An iterator that yields the topics.
    """
    topics_iter = sns.topics.all()
    return topics_iter

def subscribe(topic, protocol, endpoint):
    """
    Subscribes an endpoint to the topic. Some endpoint types, such as email,
    must be confirmed before their subscriptions are active. When a subscription
    is not confirmed, its Amazon Resource Number (ARN) is set to
    'PendingConfirmation'.

    :param topic: The topic to subscribe to.
    :param protocol: The protocol of the endpoint, such as 'sms' or 'email'.
    :param endpoint: The endpoint that receives messages, such as a phone number
                      or an email address.
    :return: The newly added subscription.
    """
    subscription = topic.subscribe(Protocol=protocol, Endpoint=endpoint, ReturnSubscriptionArn=True)
    return subscription

def unsubscribe(subscription_arn):
    """
    Unsubscribes an endpoint to the topic.
    """
    sns.unsubscribe(SubscriptionArn=subscription_arn)

def publish_message(topic, message):
    """
    Publishes a message to a topic.

    :param topic: The topic to publish to.
    :param message: The message to publish.
    :return: The ID of the message.
    """
    response = topic.publish(Message=message)
    message_id = response['MessageId']
    return message_id

if __name__ == '__main__':
    # create_topic("pythonTEST")
    topic = sns.Topic(arn='arn:aws:sns:us-east-2:869275267321:pythonTEST')
    publish_message(topic, 'testing')


