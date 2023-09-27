from flask import current_app
from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy

app = current_app
db = SQLAlchemy(app)
db.init_app(app)


class User(db.Model, UserMixin):
    user_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String, nullable=False)
    username = db.Column(db.String, nullable=False, unique=True)
    password = db.Column(db.String, nullable=False)
    gender = db.Column(db.String, nullable=False)
    trackers = db.relationship("Tracker", cascade="all", backref='user')

    def get_id(self):
        return (self.user_id)


class Tracker(db.Model):
    user_id = db.Column(db.Integer,
                        db.ForeignKey('user.user_id'),
                        nullable=False)
    tracker_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    tracker_name = db.Column(db.String, nullable=False)
    description_tracker = db.Column(db.String, nullable=False)
    type = db.Column(db.String, nullable=False)
    logs = db.relationship("Log", cascade="all", backref="tracker")

    def get_id(self):
        return (self.tracker_id)


class Log(db.Model):
    tracker_id = db.Column(db.Integer,
                           db.ForeignKey("tracker.tracker_id"),
                           nullable=False)
    log_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    log = db.Column(db.String, nullable=False)
    date_time = db.Column(db.DateTime, nullable=False)
    log_description = db.Column(db.String, nullable=False)

    def get_id(self):
        return (self.log_id)
