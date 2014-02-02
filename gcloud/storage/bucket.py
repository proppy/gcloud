from gcloud.storage import exceptions
from gcloud.storage.iterator import KeyIterator
from gcloud.storage.key import Key


class Bucket(object):
  """A class representing a Bucket on Cloud Storage.

  :type connection: :class:`gcloud.storage.connection.Connection`
  :param connection: The connection to use when sending requests.

  :type name: string
  :param name: The name of the bucket.
  """

  def __init__(self, connection=None, name=None):
    self.connection = connection
    self.name = name

  @classmethod
  def from_dict(cls, bucket_dict, connection=None):
    bucket = cls(connection=connection)
    bucket.name = bucket_dict['name']
    return bucket

  def __repr__(self):
    return '<Bucket: %s>' % self.name

  def __iter__(self):
    return iter(KeyIterator(bucket=self))

  def __contains__(self, key):
    return self.get_key(key) is not None

  @property
  def path(self):
    if not self.name:
      raise ValueError('Cannot determine path without bucket name.')

    return '/b/' + self.name

  def get_key(self, key):
    # Coerce this to a key object (either from a Key or a string).
    key = self.new_key(key)

    try:
      response = self.connection.make_request(method='GET', path=key.path,
                                              expect_json=True)
      return Key.from_dict(response, bucket=self)
    except exceptions.NotFoundError:
      return None

  def get_all_keys(self):
    return list(self)

  def new_key(self, key):
    if isinstance(key, Key):
      return key

    # Support Python 2 and 3.
    try:
      string_type = basestring
    except NameError:
      string_type = str

    if isinstance(key, string_type):
      return Key(bucket=self, name=key)

    raise TypeError('Invalid key: %s' % key)

  def delete(self):
    return self.connection.delete_bucket(self.name)

  def delete_key(self, key):
    """Deletes a key from the current bucket.

    :type key: string or :class:`gcloud.storage.key.Key`
    :param key: A key name or Key object to delete.

    :rtype: :class:`gcloud.storage.key.Key`
    :returns: The key that was just deleted.
    """

    key = self.new_key(key)
    self.connection.make_request(method='DELETE', path=key.path,
                                 expect_json=True)
    return key

  def delete_keys(self, keys):
    # TODO: What should be the return value here?
    # NOTE: boto returns a MultiDeleteResult instance.
    for key in keys:
      self.delete_key(key)
