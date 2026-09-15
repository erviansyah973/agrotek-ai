"""
AGROTEK AI — Database Models
============================
Model SQLAlchemy untuk user, request, dan log.
Database: SQLite (dev) — bisa diganti ke PostgreSQL nanti.
"""

from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

from app.extensions import db


class User(db.Model):
    __tablename__ = "users"

    id            = db.Column(db.Integer, primary_key=True)
    username      = db.Column(db.String(80), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    name          = db.Column(db.String(160), nullable=False)
    email         = db.Column(db.String(160))
    role          = db.Column(db.String(40), default="umum", nullable=False)
    active        = db.Column(db.Boolean, default=True, nullable=False)
    created_at    = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    def set_password(self, password: str):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        return {
            "id": self.id,
            "username": self.username,
            "name": self.name,
            "email": self.email,
            "role": self.role,
            "active": self.active,
        }


class DataRequest(db.Model):
    __tablename__ = "data_requests"

    id           = db.Column(db.Integer, primary_key=True)
    name         = db.Column(db.String(160), nullable=False)
    email        = db.Column(db.String(160), nullable=False)
    institution  = db.Column(db.String(200))
    dataset_slug = db.Column(db.String(120), nullable=False, index=True)
    format       = db.Column(db.String(40))
    purpose      = db.Column(db.Text)
    status       = db.Column(db.String(30), default="pending", nullable=False, index=True)
    created_at   = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at   = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "institution": self.institution,
            "dataset": self.dataset_slug,
            "format": self.format,
            "status": self.status,
            "created_at": self.created_at.strftime("%d-%m-%Y %H:%M") if self.created_at else "-",
        }


class Log(db.Model):
    __tablename__ = "logs"

    id         = db.Column(db.Integer, primary_key=True)
    level      = db.Column(db.String(20), default="info")
    source     = db.Column(db.String(80))
    message    = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)

    def to_dict(self):
        return {
            "id": self.id,
            "level": self.level,
            "source": self.source,
            "message": self.message,
            "created_at": self.created_at.strftime("%d-%m-%Y %H:%M") if self.created_at else "-",
        }