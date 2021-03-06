import json
import boto3
import os


def subscribe(origination_number, client):
    print('Subscribe: ', origination_number)

    if 'ARN_TOPIC' in os.environ:
        response = client.subscribe(
            TopicArn=os.environ['ARN_TOPIC'],
            Protocol='sms',
            Endpoint=origination_number,
            ReturnSubscriptionArn=True
        )
        print(response)
    else:
        print('Would have subscribed: ', origination_number)


def unsubscribe(origination_number, client):
    print('Unsubscribe: ', origination_number)

    arn = get_arn_from_origination_number(origination_number, client)

    if arn is not None:
        response = client.unsubscribe(
            SubscriptionArn=arn
        )
        print(response)
    else:
        print('Did not identify ARN to unsubscribe for: ', origination_number)


def get_arn_from_origination_number(origination_number, client):
    if 'ARN_TOPIC' in os.environ:
        response = client.list_subscriptions_by_topic(
            TopicArn=os.environ['ARN_TOPIC']
        )
        print(response)

        all_arns = list(response.values())[0]

        for i in range(len(all_arns)):
            subscription = all_arns[i]
            phone_number = subscription.get('Endpoint')

            if phone_number == origination_number:
                arn_to_be_unsubscribed = subscription.get('SubscriptionArn')
                print('arn: ', arn_to_be_unsubscribed)
                return arn_to_be_unsubscribed
    else:
        print('Would have retrieved subscription arn from origination number: ', origination_number)

    return None


def lambda_handler(event, context):
    print('Received event: ', event)

    confirm_keyword = os.environ['confirmKeyword'].lower() if 'confirmKeyword' in os.environ else 'default_confirm_key'
    unsubscribe_keyword = os.environ[
        'unsubscribeKeyword'].lower() if 'unsubscribeKeyword' in os.environ else 'default_unsubscribe_key'

    message = list(event.values())[0][-1].get('Sns').get('Message')
    print('message: ', message)

    origination_number = list(json.loads(message).values())[0]
    print('originationNumber: ', origination_number)

    message_body = list(json.loads(message).values())[3].lower()
    print('messageBody: ', message_body)

    client = boto3.client('sns')

    if message_body.find(confirm_keyword) != -1:
        subscribe(origination_number, client)

    elif message_body.find(unsubscribe_keyword) != -1:
        unsubscribe(origination_number, client)

    else:
        print('Payload contained no key words')


# remove below for deployment
def main():
    lambda_handler(None, None)


main()
