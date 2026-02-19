from . import db
from flask_login import UserMixin
from datetime import datetime

class User(UserMixin,db.Model):
    id=db.Column(db.Integer,primary_key=True)
    username=db.Column(db.String(80),unique=True,nullable=False)
    email=db.Column(db.String(120),unique=True,nullable=False)
    password=db.Column(db.String(128),nullable=False)
    role=db.Column(db.String(20),nullable=False)

    company_profile=db.relationship('Company',backref='user',uselist=False)
    student_profile=db.relationship('Student',backref='user',uselist=False)


class Company(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    user_id=db.Column(db.Integer,db.ForeignKey('user.id'),nullable=False)
    company_name=db.Column(db.String(100),nullable=False)
    location=db.Column(db.String(100))
    description=db.Column(db.String(500))
    website=db.Column(db.String(100))
    is_approved=db.Column(db.Boolean,default=False) 
    jobs=db.relationship('Job',backref='company',uselist=False)

class Student(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    user_id=db.Column(db.Integer,db.ForeignKey('user.id'),nullable=False)
    name=db.Column(db.String(100),nullable=False)
    roll_no=db.Column(db.String(20),unique=True,nullable=False)
    branch=db.Column(db.String(100))
    cgpa=db.Column(db.Float)
    resume_url=db.Column(db.String(200))
    applications=db.relationship('Applications',backref='student',lazy=True)

class Job(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    company_id=db.Column(db.Integer,db.ForeignKey('company.id'),nullable=False)
    title=db.Column(db.String(100),nullable=False)
    description=db.Column(db.Text)
    requirements=db.Column(db.Text)
    deadline=db.Column(db.DateTime,nullable=False)
    salary=db.Column(db.String(50))
    status=db.Column(db.String(20),default='Pending')
    applications=db.relationship('Applications',backref='job',lazy=True)

class Applications(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    job_id=db.Column(db.Integer,db.ForeignKey('job.id'),nullable=False)
    student_id=db.Column(db.Integer,db.ForeignKey('student.id'),nullable=False)
    date_applied=db.Column(db.DateTime,nullable=False,default=datetime.utcnow)
    status=db.Column(db.String(20),default='Applied')

    
    


