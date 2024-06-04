import configparser
from mongoengine import connect


config = configparser.ConfigParser()
# config.read('config_local.ini')
config.read('config_atlas.ini')
uri = config.get('DB', 'uri')

connect(host=uri)
