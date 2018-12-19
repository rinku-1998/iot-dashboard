from app import db, login
from datetime import datetime
from datetime import timedelta
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

class Car(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    number_plate = db.Column(db.String(8), index=True, unique=True)
    entry_time = db.Column(db.DateTime, index=True)
    depart_time = db.Column(db.DateTime, index=True)

    def __repr__(self):
        return 'number_plate={}'.format(self.number_plate)

    def set_entrytime(self):
        self.entry_time = datetime.utcnow()

    def set_departtime(self):
        self.depart_time = datetime.utcnow()

    def reset_departtime(self):
        self.depart_time = None
    
    def get_entrytime(self):
        return self.entry_time.replace(microsecond=0).isoformat(' ')

    def get_departtime(self):
        if self.depart_time is None:
            return '尚未離開'
        else:
            return self.depart_time.replace(microsecond=0).isoformat(' ')
    
    def get_status(self):
        if self.depart_time is None:
            base_time = datetime.utcnow()-self.entry_time
        else:
            base_time = self.depart_time - self.entry_time
        
        days, seconds = base_time.days, base_time.seconds
        hours = days * 24 + seconds // 3600
        return days


    def get_passedtime(self):
        if self.depart_time is None:
            base_time = datetime.utcnow()-self.entry_time
        else:
            base_time = self.depart_time - self.entry_time
        
        days, seconds = base_time.days, base_time.seconds
        hours = days * 24 + seconds // 3600
        hours = hours % 24
        minutes = (seconds % 3600) // 60
        seconds = seconds % 60
        if days > 0:
            return '{:d}天 {:d}小時 {:02d}分 {:02d}秒'.format( days, hours, minutes, seconds)
        else:
            return '{:d}小時 {:02d}分 {:02d}秒'.format(hours, minutes, seconds)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))

    def __repr__(self):
        return '<User {}>'.format(self.username)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


@login.user_loader
def load_user(id):
    return User.query.get(int(id))
        