class Bucket(object):

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
