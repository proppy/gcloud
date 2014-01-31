import os.path

from gcloud import storage


__all__ = ['CLIENT_EMAIL', 'PRIVATE_KEY_PATH', 'PROJECT_NAME',
           'get_connection', 'main']


CLIENT_EMAIL = '606734090113-6ink7iugcv89da9sru7lii8bs3i0obqg@developer.gserviceaccount.com'
PRIVATE_KEY_PATH = os.path.join(os.path.dirname(storage.__file__), 'demo.key')
PROJECT_NAME = 'gcloud-storage-demo'


def get_connection():
  return storage.get_connection(PROJECT_NAME, CLIENT_EMAIL, PRIVATE_KEY_PATH)


def main():
  pass


if __name__ == '__main__':
  main()
