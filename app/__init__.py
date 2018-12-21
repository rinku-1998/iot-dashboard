import eventlet
from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_socketio import SocketIO
from flask_mqtt import Mqtt
from flask_login import LoginManager
from flask_moment import Moment


eventlet.monkey_patch()

app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
login = LoginManager(app)
login.login_view = 'login'
socketio = SocketIO(app)
mqtt = Mqtt(app)
moment = Moment(app)


from app import routes, models, errors

if __name__ == '__main__':
    socketio.run(app, debug=True)