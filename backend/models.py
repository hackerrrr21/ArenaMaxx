"""
models.py — SQLAlchemy ORM Models for ArenaMaxx Stadium Platform.

Defines the relational data schema for all stadium entities:
  - User: Attendees and management staff (Firebase Auth-compatible).
  - Seat: Physical seating inventory across stadium blocks.
  - Ticket: Links a purchased Seat to a User.
  - Order: Concession/food orders with virtual queue management.
  - WashroomSlot: Timed washroom reservations to reduce physical queuing.
"""

from __future__ import annotations
import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class User(db.Model):
    """
    Represents a stadium attendee or management staff member.

    Attributes:
        id: Auto-incremented primary key.
        firebase_uid: Optional Firebase Auth UID for cloud authentication.
        name: Display name of the user.
        role: User role — 'attendee' or 'management'.
    """
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    firebase_uid = db.Column(db.String(128), unique=True, nullable=True)
    name = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(20), default='attendee')

    def __repr__(self) -> str:
        return f"<User id={self.id} name='{self.name}' role='{self.role}'>"


class Seat(db.Model):
    """
    Represents a physical seat in the stadium seating inventory.

    Attributes:
        id: Auto-incremented primary key.
        block: Stadium block identifier (e.g., 'A', 'B', 'VIP').
        row: Row identifier within the block (e.g., '1', '2', 'A').
        number: Seat number within the row.
        status: Availability status — 'Available', 'Selected', or 'Sold'.
    """
    __tablename__ = 'seat'

    id = db.Column(db.Integer, primary_key=True)
    block = db.Column(db.String(10), nullable=False, index=True)
    row = db.Column(db.String(5), nullable=False)
    number = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(20), default='Available')

    def __repr__(self) -> str:
        return f"<Seat Block={self.block} Row={self.row} No={self.number} Status={self.status}>"


class Ticket(db.Model):
    """
    Represents a confirmed ticket linking a User to a Seat.

    Attributes:
        id: Auto-incremented primary key.
        user_id: Foreign key to the User who purchased the ticket.
        seat_id: Foreign key to the reserved Seat.
        purchase_time: UTC timestamp of when the ticket was issued.
    """
    __tablename__ = 'ticket'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    seat_id = db.Column(db.Integer, db.ForeignKey('seat.id'), nullable=False)
    purchase_time = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    user = db.relationship('User', backref='tickets')
    seat = db.relationship('Seat', backref='ticket')

    def __repr__(self) -> str:
        return f"<Ticket id={self.id} user={self.user_id} seat={self.seat_id}>"


class Order(db.Model):
    """
    Represents a concession/food order placed by an attendee.

    Utilises a virtual queue system to reduce physical wait times at counters.

    Attributes:
        id: Auto-incremented primary key.
        user_id: Foreign key to the User who placed the order.
        items: String description of ordered items (e.g., '2x Vada Pav, 1x Coffee').
        status: Order lifecycle status — 'Preparing', 'Ready', or 'Dispatched'.
        queue_number: Unique monotonically-increasing virtual queue position.
        created_at: UTC timestamp when the order was placed.
    """
    __tablename__ = 'order'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    items = db.Column(db.String(500), nullable=False)
    status = db.Column(db.String(20), default='Preparing')
    queue_number = db.Column(db.Integer, nullable=False, unique=True, index=True)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    user = db.relationship('User', backref='orders')

    def __repr__(self) -> str:
        return f"<Order #{self.queue_number} status='{self.status}' items='{self.items[:30]}'>"


class WashroomSlot(db.Model):
    """
    Represents a timed washroom reservation made by a stadium attendee.

    Slot-based booking removes physical queuing and reduces congestion at
    high-demand washroom blocks during peak match times.

    Attributes:
        id: Auto-incremented primary key.
        user_id: Foreign key to the User who made the booking.
        block: Washroom block identifier (e.g., 'Block_A', 'Block_B_w').
        time_slot: Requested time window (e.g., 'Now', 'Next Available', '14:30').
        status: Booking lifecycle — 'Booked', 'CheckedIn', or 'Completed'.
    """
    __tablename__ = 'washroom_slot'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    block = db.Column(db.String(20), nullable=False)
    time_slot = db.Column(db.String(50), nullable=False)
    status = db.Column(db.String(20), default='Booked')

    user = db.relationship('User', backref='washroom_slots')

    def __repr__(self) -> str:
        return f"<WashroomSlot block='{self.block}' slot='{self.time_slot}' status='{self.status}'>"
