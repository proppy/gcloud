"""Shortcut methods for getting set up with Google Cloud Storage.

You'll typically use these to get started with the API:

>>> import gcloud.storage
>>> bucket = gcloud.storage.get_bucket('bucket-id-here',
                                       'long-email@googleapis.com',
                                       '/path/to/private.key')
>>> # Then do other things...
>>> with bucket.get_file('/path/to/file.txt') as f:
>>>   print f
>>> bucket.upload_file('/remote/path/storage.txt', '/local/path.txt')

The main concepts with this API are:

- :class:`gcloud.storage.connection.Connection`
  which represents a connection between your machine
  and the Cloud Storage API.

- :class:`gcloud.storage.bucket.Bucket`
  which represents a particular bucket
  (akin to a mounted disk on a computer).

- ?? :class:`gcloud.storage.key.Key`
  which represents a pointer
  to a particular entity in Cloud Storage
  (akin to a file path on a remote machine).
"""


__version__ = '0.1'


def get_connection(client_email, private_key_path):
  """Shortcut method to establish a connection to Cloud Storage.

  Use this if you are going to access several buckets
  with the same set of credentials:

  >>> from gcloud import storage
  >>> connection = storage.get_connection(email, key_path)
  >>> bucket1 = connection.bucket('bucket1')
  >>> bucket2 = connection.bucket('bucket2')

  :type client_email: string
  :param client_email: The e-mail attached to the service account.

  :type private_key_path: string
  :param private_key_path: The path to a private key file (this file was
                           given to you when you created the service
                           account).

  :rtype: :class:`gcloud.storage.connection.Connection`
  :returns: A connection defined with the proper credentials.
  """
  from connection import Connection
  from credentials import Credentials

  credentials = Credentials.get_for_service_account(
      client_email, private_key_path)
  return Connection(credentials=credentials)

def get_bucket(bucket_id, client_email, private_key_path):
  """Shortcut method to establish a connection to a particular bucket.

  You'll generally use this as the first call to working with the API:

  >>> from gcloud import storage
  >>> bucket = storage.get_bucket('bucket-id', email, key_path)
  >>> # Now you can do things with the bucket.
  >>> bucket.exists('/path/to/file.txt')
  False

  :type bucket_id: string
  :param bucket_id: The id of the bucket you want to use.
                    This is akin to a disk name on a file system.

  :type client_email: string
  :param client_email: The e-mail attached to the service account.

  :type private_key_path: string
  :param private_key_path: The path to a private key file (this file was
                           given to you when you created the service
                           account).

  :rtype: :class:`gcloud.storage.bucket.Bucket`
  :returns: A bucket with a connection using the provided credentials.
  """
  connection = get_connection(client_email, private_key_path)
  return connection.bucket(bucket_id)
