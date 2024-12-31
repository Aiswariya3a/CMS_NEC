from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

# Trainer model
class Trainer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False, unique=True)
    expertise = db.Column(db.String(100), nullable=False)
    sessions = db.relationship('Session', backref='trainer', lazy=True)

# Session model
class Session(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    date = db.Column(db.Date, nullable=False)
    start_time = db.Column(db.String(5), nullable=False)
    end_time = db.Column(db.String(5), nullable=False)
    trainer_id = db.Column(db.Integer, db.ForeignKey('trainer.id'), nullable=False)
    students = db.relationship('Student', secondary='attendance', backref='sessions', lazy='dynamic')
    engagement_reports = db.relationship('EngagementReport', back_populates='session')

# Student model
class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False, unique=True)

# Attendance model (many-to-many relationship between Students and Sessions)
class Attendance(db.Model):
    __tablename__ = 'attendance'
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, db.ForeignKey('session.id'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    present = db.Column(db.Boolean, default=False) 
    session = db.relationship('Session', backref=db.backref('attendance_records', lazy=True))
    student = db.relationship('Student', backref=db.backref('attendance_records', lazy=True))


class EngagementReport(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, db.ForeignKey('session.id'), nullable=False)
    score = db.Column(db.Float, nullable=False)
    report_content = db.Column(db.Text, nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    session = db.relationship('Session', back_populates='engagement_reports')
