import httplib2
import json


from gcloud import connection
from gcloud.storage import exceptions
from gcloud.storage.bucket import Bucket


# TODO: Document this class.
class Connection(connection.Connection):
  """A connection to Google Cloud Storage via the JSON REST API.

  This class should understand only the basic types (and protobufs)
  in method arguments, however should be capable of returning advanced types.

  :type credentials: :class:`gcloud.datastore.credentials.Credentials`
  :param credentials: The OAuth2 Credentials to use for this connection.
  """

  API_VERSION = 'v1beta2'
  """The version of the API, used in building the API call's URL."""

  API_URL_TEMPLATE = '{api_base_url}/storage/{api_version}{path}'
  """A template used to craft the URL pointing toward a particular API call."""

  def __init__(self, project_name, *args, **kwargs):
    super(Connection, self).__init__(*args, **kwargs)

    self.project_name = project_name

  # TODO: Fix these arguments. There is cruft here.
  def make_request(self, method, path, bucket=None, key=None,
                   data=None, api_base_url=None, api_version=None):
    """Make a request over the Http transport to the Cloud Datastore API.

    :type method: string
    :param method: The HTTP method name (ie, ``GET``, ``POST``, etc)

    :raises: Exception if the response code is not 200 OK.
    """

    headers = {
        'Accept-Encoding': 'gzip',
        }

    url = self.API_URL_TEMPLATE.format(
        api_base_url=(api_base_url or self.API_BASE_URL),
        api_version=(api_version or self.API_VERSION),
        path=path)

    # TODO: Use urlparse for this.
    url += '?project=' + self.project_name

    if data:
      data = json.dumps(data)
      headers.update({
        'Content-Type': 'application/json',
        'Content-Length': str(len(data)),
        })

    response_headers, content = self.http.request(
        uri=url, method=method, headers=headers, body=data)

    # TODO: Better error handling.
    status = response_headers['status']
    if status == '404':
      raise exceptions.NotFoundError(response_headers, content)
    elif not status.startswith('2'):
      raise exceptions.Error(response_headers, content)

    return json.loads(content)

  def __iter__(self):
    for bucket in self.get_all_buckets():
      yield bucket

  def __contains__(self, bucket_name):
    return self.lookup(bucket_name) is not None

  def get_all_buckets(self, *args, **kwargs):
    response = self.make_request(method='GET', path='/b')
    return [Bucket.from_dict(b, connection=self) for b in response['items']]

  def get_bucket(self, bucket_name, *args, **kwargs):
    # TODO: URL-encode the bucket name to be safe?
    response = self.make_request(method='GET', path='/b/%s' % bucket_name)
    return Bucket.from_dict(response, connection=self)

  def lookup(self, bucket_name):
    try:
      return self.get_bucket(bucket_name)
    except exceptions.NotFoundError:
      return None

  def create_bucket(self, bucket_name, *args, **kwargs):
    response = self.make_request(method='POST', path='/b', data={'name': bucket_name})
    return Bucket.from_dict(response, connection=self)

  def delete_bucket(self, bucket_name, *args, **kwargs):
    response = self.make_request(method='DELETE', path='/b/%s' % bucket_name)
    return True
