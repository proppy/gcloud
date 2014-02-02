class Key(object):
  """A wrapper around Cloud Storage's concept of an ``Object``.

  :type bucket: :class:`gcloud.storage.bucket.Bucket`
  :param bucket: The bucket to which this key belongs.

  :type name: string
  :param name: The name of the key.
               This corresponds to the unique path of the object
               in the bucket.

  :type extra_data: dict
  :param extra_data: All the other data provided by Cloud Storage
                     in case we need to use it at some point.
  """

  def __init__(self, bucket=None, name=None, extra_data=None):
    self.bucket = bucket
    self.name = name
    self.extra_data = extra_data or {}

  @classmethod
  def from_dict(cls, key_dict, bucket=None):
    """Instantiate a :class:`Key` from data returned by the JSON API.

    :type key_dict: dict
    :param key_dict: A dictionary of data returned from
                     getting an Cloud Storage object.

    :type bucket: :class:`gcloud.storage.bucket.Bucket`
    :param bucket: The bucket to which this key belongs
                   (and by proxy, which connection to use).

    :rtype: :class:`Key`
    :returns: A key based on the data provided.
    """

    return cls(bucket=bucket, name=key_dict['name'], extra_data=key_dict)

  def __repr__(self):
    if self.bucket:
      bucket_name = self.bucket.name
    else:
      bucket_name = None

    return '<Key: %s, %s>' % (bucket_name, self.name)

  @property
  def path(self):
    """Getter property for the URL path to this Key.

    :rtype: string
    :returns: The URL path to this Key.
    """

    if not self.bucket:
      raise ValueError('Cannot determine path without a bucket defined.')
    elif not self.name:
      raise ValueError('Cannot determine path without a key name.')

    return self.bucket.path + '/o/' + self.name

  @property
  def connection(self):
    """Getter property for the connection to use with this Key.

    :rtype: :class:`gcloud.storage.connection.Connection` or None
    :returns: The connection to use, or None if no connection is set.
    """

    # TODO: If a bucket isn't defined, this is basically useless.
    #       Where do we throw an error?
    if self.bucket and self.bucket.connection:
      return self.bucket.connection

  def exists(self):
    """Determines whether or not this key exists.

    :rtype: bool
    :returns: True if the key exists in Cloud Storage.
    """

    return self.bucket.get_key(self.name) is not None

  def delete(self):
    """Deletes a key from Cloud Storage.

    :rtype: :class:`Key`
    :returns: The key that was just deleted.
    """

    return self.bucket.delete_key(self)

  def set_contents_from_string(self, data):
    """Sets the contents of this key to the provided string.

    :type data: string
    :param data: The data to store in this key.

    :rtype: :class:`Key`
    :returns: The updated Key object.
    """

    # TODO: How do we handle NotFoundErrors?
    response = self.connection.make_request(
        method='POST', path=self.bucket.path + '/o',
        api_base_url=self.connection.API_BASE_URL + '/upload',
        query_params={'uploadType': 'media', 'name': self.name},
        data=data, content_type='text/plain', expect_json=True)
    return self.from_dict(response)

  def get_contents_as_string(self):
    """Gets the data stored on this Key as a string.

    :rtype: string
    :returns: The data stored in this key.
    """

    # TODO: If not found, should this raise an exception? or return None?
    response = self.connection.make_request(
        method='GET', path=self.path, query_params={'alt': 'media'})
    return response
