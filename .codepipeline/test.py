import os
import boto3
import sys


def list_buckets():
    session = boto3.Session()
    s3 = session.resource('s3')

    bucket = s3.Bucket(os.environ.get('GOVUK_ALERTS_S3_BUCKET_NAME'))

    for bucket_object in bucket.objects.all():
        sys.stdout.write(bucket_object.key)
