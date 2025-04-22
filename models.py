from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    email = db.Column(db.String(120), primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # 'admin' or 'member'
    tasks = db.relationship('Task', backref='assigned_to_user', lazy=True)
    comments = db.relationship('Comment', backref='author', lazy=True)

class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    tasks = db.relationship('Task', backref='project', lazy=True)

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text)
    status = db.Column(db.String(20), default="Pending")
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'))
    assigned_to_email = db.Column(db.String(120), db.ForeignKey('user.email'))

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    user_email = db.Column(db.String(120), db.ForeignKey('user.email'))
    task_id = db.Column(db.Integer, db.ForeignKey('task.id'))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

class File(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(100), nullable=False)
    task_id = db.Column(db.Integer, db.ForeignKey('task.id'))