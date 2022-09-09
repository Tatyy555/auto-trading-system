import configparser

conf = configparser.ConfigParser()
conf.read('settings.ini')

access_key = conf['coincheck']['access_key']
secret_key = conf['coincheck']['secret_key']
LINE_access_token = conf['LINE']['LINE_access_token']
