import httplib2
import json
import urllib


from gcloud import connection
from gcloud.storage import exceptions
from gcloud.storage.bucket import Bucket
from gcloud.storage.iterator import BucketIterator


class Connection(connection.Connection):
  """A connection to Google Cloud Storage via the JSON REST API.

  This class should understand only the basic types (and protobufs)
  in method arguments, however should be capable of returning advanced types.

  See :class:`gcloud.connection.Connection` for a full list of parameters.

  :type project_name: string
  :param project_name: The project name to connect to.
  """

  API_VERSION = 'v1beta2'
  """The version of the API, used in building the API call's URL."""

  API_URL_TEMPLATE = '{api_base_url}/storage/{api_version}{path}'
  """A template used to craft the URL pointing toward a particular API call."""

  def __init__(self, project_name, *args, **kwargs):
    super(Connection, self).__init__(*args, **kwargs)

    self.project_name = project_name

  def __iter__(self):
    return iter(BucketIterator(connection=self))

  def __contains__(self, bucket_name):
    return self.lookup(bucket_name) is not None

  def make_request(self, method, path=None, url=None, query_params=None,
                   data=None, content_type='text/plain',
                   api_base_url=None, api_version=None,
                   expect_json=False):
    """Make a request over the Http transport to the Cloud Datastore API.

    :type method: string
    :param method: The HTTP method name (ie, ``GET``, ``POST``, etc)

    :raises: Exception if the response code is not 200 OK.
    """

    headers = {
        'accept-encoding': 'gzip',
        }

    url = self.API_URL_TEMPLATE.format(
        api_base_url=(api_base_url or self.API_BASE_URL),
        api_version=(api_version or self.API_VERSION),
        path=path)

    query_params = query_params or {}
    query_params.update({'project': self.project_name})
    url += '?' + urllib.urlencode(query_params)

    if data:
      # Making the executive decision that any dictionary
      # data will be JSON.
      if isinstance(data, dict):
        data = json.dumps(data)
        content_type = 'application/json'

      headers['content-length'] = str(len(str(data)))
      if content_type:
        headers['content-type'] = content_type

    response_headers, content = self.http.request(
        uri=url, method=method, headers=headers, body=data)

    # TODO: Add better error handling.
    status = response_headers['status']
    if status == '404':
      raise exceptions.NotFoundError(response_headers, content)
    elif not status.startswith('2'):
      raise exceptions.ConnectionError(response_headers, content)

    if not content:
      return

    if expect_json:
      # TODO: Better checking on this header for JSON.
      content_type = response_headers.get('content-type', '')
      if not content_type.startswith('application/json'):
        raise TypeError('Expected JSON, got %s' % content_type)
      return json.loads(content)
    else:
      return content

  def get_all_buckets(self, *args, **kwargs):
    return list(self)

  def get_bucket(self, bucket_name, *args, **kwargs):
    # TODO: URL-encode the bucket name to be safe?
    response = self.make_request(method='GET', path=self.path, expect_json=True)
    return Bucket.from_dict(response, connection=self)

  def lookup(self, bucket_name):
    try:
      return self.get_bucket(bucket_name)
    except exceptions.NotFoundError:
      return None

  def create_bucket(self, bucket, *args, **kwargs):
    bucket = self.new_bucket(bucket)
    response = self.make_request(method='POST', path='/b',
                                 data={'name': bucket.name},
                                 expect_json=True)
    return Bucket.from_dict(response, connection=self)

  def delete_bucket(self, bucket, *args, **kwargs):
    bucket = self.new_bucket(bucket)
    response = self.make_request(method='DELETE', path=bucket.path,
                                 expect_json=True)
    return True

  def new_bucket(self, bucket):
    if isinstance(bucket, Bucket):
      return bucket

    # Support Python 2 and 3.
    try:
      string_type = basestring
    except NameError:
      string_type = str

    if isinstance(bucket, string_type):
      return Bucket(connection=self, name=bucket)

    raise TypeError('Invalid bucket: %s' % bucket)
