import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you will never guess'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    #MQTT_BROKER_URL = '192.168.198.132'
    MQTT_BROKER_URL = '137.116.170.68'
    MQTT_BROKER_PORT = 1883
    MQTT_REFRESH_TIME = 1.0  # refresh time in seconds
    MQTT_USERNAME = ''  # set the username here if you need authentication for the broker
    MQTT_PASSWORD = ''  # set the password here if the broker demands authentication
    MQTT_KEEPALIVE = 5  # set the time interval for sending a ping to the broker to 5 seconds
    MQTT_TLS_ENABLED = False  # set TLS to disabled for testing purposes