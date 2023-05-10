import os
import sys

import boto3


def test():
    sqs_client = boto3.client('sqs')
    queue = sqs_client.create_queue(QueueName='test', Attributes={'DelaySeconds': '5'})
    sys.stdout.write(queue.url)


def list_buckets():
    session = boto3.Session()
    s3 = session.resource('s3')

    bucket = s3.Bucket(os.environ.get('GOVUK_ALERTS_S3_BUCKET_NAME'))

    for bucket_object in bucket.objects.all():
        sys.stdout.write(bucket_object.key)


test()
