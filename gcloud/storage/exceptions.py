# TODO: Make these super useful.

class ConnectionError(Exception):

  def __init__(self, response_headers, content):
    message = str(response_headers) + content

    Exception.__init__(self, message)

class NotFoundError(ConnectionError):
  # TODO: Make this accept the URL of the thing that wasn't found.
  pass
