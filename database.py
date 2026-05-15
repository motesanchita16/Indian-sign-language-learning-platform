from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

# ---------------- USER TABLE ----------------
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=   True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    is_active = db.Column(db.Boolean, default=True)

# ---------------- PROGRESS TABLE ----------------
class UserProgress(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100))
    score = db.Column(db.Integer)
    date = db.Column(db.DateTime, default=datetime.utcnow)

# ---------------- ADMIN HELPERS ----------------
def count_users():
    return User.query.count()

def count_active_users():
    return User.query.filter_by(is_active=True).count()

# ---------------- SQLITE RAW ACCESS (OPTIONAL) ----------------
def get_db():
    import sqlite3
    conn = sqlite3.connect("progress.db")
    conn.row_factory = sqlite3.Row
    return conn
