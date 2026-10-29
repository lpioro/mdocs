from datetime import datetime, timezone
from flask_login import UserMixin
from . import db

def now():
    return datetime.now(timezone.utc)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False, unique=True)
    password_hash = db.Column(db.String(255), nullable=False)

class Client(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), nullable=False)
    nip = db.Column(db.String(10), unique=True)
    email = db.Column(db.String(255))
    active = db.Column(db.Boolean, default=True, nullable=False)
    senders = db.relationship("Sender", backref="client", cascade="all, delete-orphan")
    documents = db.relationship("Document", backref="client", cascade="all, delete-orphan")

class Sender(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    client_id = db.Column(db.Integer, db.ForeignKey("client.id"), nullable=False)

class EmailMessage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sender = db.Column(db.String(255), nullable=False)
    subject = db.Column(db.String(255), nullable=False)
    received_at = db.Column(db.DateTime(timezone=True), default=now, nullable=False)
    client_id = db.Column(db.Integer, db.ForeignKey("client.id"))
    client = db.relationship("Client")

class Document(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey("client.id"), nullable=False)
    name = db.Column(db.String(255), nullable=False)
    kind = db.Column(db.String(100), nullable=False, default="Inny")
    period = db.Column(db.String(7), nullable=False)
    received_at = db.Column(db.DateTime(timezone=True), default=now, nullable=False)

class Reminder(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey("client.id"), nullable=False)
    client = db.relationship("Client")
    period = db.Column(db.String(7), nullable=False)
    message = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), default=now, nullable=False)
