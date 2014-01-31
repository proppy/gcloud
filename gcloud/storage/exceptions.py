class ConnectionError(Exception):

  def __init__(self, response_headers, content):
    message = str(response_headers) + content

    Exception.__init__(self, message)

class NotFoundError(ConnectionError):
  pass
