import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    firebase_uid = db.Column(db.String(128), unique=True, nullable=True) # Optional for mock
    name = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(20), default='attendee') # attendee or management

class Seat(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    block = db.Column(db.String(10), nullable=False)
    row = db.Column(db.String(5), nullable=False)
    number = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(20), default='Available') # Available, Selected, Sold

class Ticket(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    seat_id = db.Column(db.Integer, db.ForeignKey('seat.id'), nullable=False)
    purchase_time = db.Column(db.DateTime, default=datetime.datetime.utcnow)

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    items = db.Column(db.String(500), nullable=False) # JSON literal of items
    status = db.Column(db.String(20), default='Preparing') # Preparing, Ready, Dispatched
    queue_number = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)

class WashroomSlot(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    block = db.Column(db.String(20), nullable=False)
    time_slot = db.Column(db.String(50), nullable=False)
    status = db.Column(db.String(20), default='Booked') # Booked, CheckedIn, Completed
