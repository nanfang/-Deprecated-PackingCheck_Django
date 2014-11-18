import boto
from boto.s3.connection import OrdinaryCallingFormat
from django.conf import settings


class S3Exception(Exception):
    pass


class S3Storage(object):
    def __init__(self, aws_access_key_id, aws_secret_access_key,
                 host='s3.amazonaws.com', port=None, is_secure=False):
        self.aws_access_key_id = aws_access_key_id
        self.aws_secret_access_key = aws_secret_access_key
        self.host = host
        self.port = port
        self.is_secure = is_secure
        self.conn = None

    def get_connection(self):
        if not self.conn:
            self.conn = boto.connect_s3(
                aws_access_key_id=self.aws_access_key_id,
                aws_secret_access_key=self.aws_secret_access_key,
                host=self.host,
                port=self.port,
                is_secure=self.is_secure,
                calling_format=OrdinaryCallingFormat()
            )
        return self.conn

    def get_file_size(self, bucket_name, key_name, content_type=None):
        try:
            if not self.exists(bucket_name, key_name):
                return None

            bucket = self.get_connection().get_bucket(bucket_name, validate=False)
            key = bucket.get_key(key_name)

            if content_type:
                key.set_metadata("Content-Type", content_type)

            return key.size
        except boto.exception.S3ResponseError as ex:
            if ex.status == 404:
                return None
            else:
                raise S3Exception(ex)
        except Exception as ex:
            raise S3Exception(ex)

    def get_file_md5(self, bucket_name, key_name, content_type=None):
        try:
            if not self.exists(bucket_name, key_name):
                return None

            bucket = self.get_connection().get_bucket(bucket_name, validate=False)
            key = bucket.get_key(key_name)

            if content_type:
                key.set_metadata("Content-Type", content_type)

            # '"948fafedb5b6fec6ba"' to remove "
            return key.etag.replace('"', '')
        except boto.exception.S3ResponseError as ex:
            if ex.status == 404:
                return None
            else:
                raise S3Exception(ex)
        except Exception as ex:
            raise S3Exception(ex)

    def get(self, bucket_name, key_name, content_type=None, retry_count=0,
            retry_delay=10):
        try:
            bucket = self.get_connection().get_bucket(
                bucket_name, validate=False
            )
            key = bucket.new_key(key_name)
            if content_type:
                key.set_metadata("Content-Type", content_type)
            return key.get_contents_as_string()
        except boto.exception.S3ResponseError as ex:
            if ex.status == 404:
                return None
            else:
                raise S3Exception(ex)
        except Exception as ex:
            raise S3Exception(ex)

    def copy(self, dst_bucket, dst_key, src_bucket, src_key):
        bucket = self.get_connection().get_bucket(dst_bucket, validate=False)
        try:
            bucket.copy_key(dst_key, src_bucket, src_key)
            return True
        except Exception as ex:
            raise S3Exception(ex)

    def exists(self, bucket_name, key_name):
        try:
            bucket = self.get_connection().get_bucket(bucket_name,
                                                      validate=False)
            key = bucket.get_key(key_name)
            return key is not None
        except Exception as ex:
            raise S3Exception(ex)

    def put(self, bucket_name, key_name, data, content_type=None,
            public=False, retry_count=0, retry_delay=10):  # in seconds
        key = None
        try:
            bucket = self.get_connection().get_bucket(bucket_name,
                                                      validate=False)
            key = bucket.new_key(key_name)
            if content_type:
                key.set_metadata("Content-Type", content_type)
            key.set_contents_from_string(data)
            if public:
                key.make_public()
        except Exception as ex:
            raise S3Exception(ex)

    def get_url(self, bucket_name, key_name, expires_in=84600):
        """Generatre url of object in S3"""
        try:
            bucket = self.get_connection().get_bucket(bucket_name, validate=False)
            key = bucket.get_key(key_name)
            if key is None:
                raise Exception("Found new key name: %s" % key_name)
            return key.generate_url(expires_in)
        except Exception as ex:
            raise S3Exception(ex)

    def make_private(self, bucket_name):
        """Make all files in the specified bucket to be private."""
        bucket = self.get_connection().get_bucket(bucket_name, validate=False)
        for key in bucket.list():
            print 'make %s to be private' % key.name
            key.set_acl('private')

    def delete(self, bucket_name, key_name):
        try:
            bucket = self.get_connection().get_bucket(bucket_name, validate=False)
            key = bucket.new_key(key_name)
            key.delete()
        except Exception as ex:
            raise S3Exception(ex)

    def list(self, bucket_name, prefix=''):
        try:
            bucket = self.get_connection().get_bucket(bucket_name, validate=False)
            for key in bucket.list(prefix=prefix):
                yield key.name
        except Exception as ex:
            raise S3Exception(ex)


s3_storage = S3Storage(
    aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
    aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
    host=settings.AWS_HOST,
    port=settings.AWS_PORT,
    is_secure=settings.AWS_SECURE,
)