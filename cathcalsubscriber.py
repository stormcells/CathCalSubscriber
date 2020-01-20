import json
import boto3
import os


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
        print('Subscribe... ', origination_number)
        response = client.subscribe(
            TopicArn=os.environ['ARN_TOPIC'],
            Protocol='sms',
            Endpoint=origination_number,
            ReturnSubscriptionArn=True
        )
        print(response)
        return response

    elif message_body.find(unsubscribe_keyword) != -1:
        print('Unsubscribe... ', origination_number)
        response = client.list_subscriptions_by_topic(
            TopicArn=os.environ['ARN_TOPIC']
        )
        print(response)

        all_arns = list(response.values())[0]

        arn_to_be_unsubscribed = ''
        for i in range(len(all_arns)):
            val = all_arns[i]
            phone_number = val.get('Endpoint')
            if phone_number == origination_number:
                arn_to_be_unsubscribed = val.get('SubscriptionArn')
                print('arn: ', arn_to_be_unsubscribed)

        if arn_to_be_unsubscribed != '':
            response = client.unsubscribe(
                SubscriptionArn=arn_to_be_unsubscribed
            )
        print(response)
        return response
    else:
        print('Payload contained no key words')
