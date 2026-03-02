from flask_wtf import FlaskForm
from wtforms import StringField,PasswordField,FloatField,SubmitField,TextAreaField,DateField
from wtforms.validators import DataRequired,Length,Email,EqualTo,URL,ValidationError
from .models import User
from datetime import date


class StudentRegistrationForm(FlaskForm):
    username = StringField('username', validators=[DataRequired(),Length(min=2,max=20)])
    name=StringField('name',validators=[DataRequired()])
    email=StringField('email',validators=[DataRequired(),Email()])
    password=PasswordField('password',validators=[DataRequired()])
    confirm_password=PasswordField('confirm_password',validators=[DataRequired(),EqualTo('password')])
    cgpa=FloatField('cgpa',validators=[DataRequired()])
    branch=StringField('branch',validators=[DataRequired()])
    roll_no=StringField('roll_no',validators=[DataRequired()])
    resume_url=StringField('resume_url',validators=[DataRequired()])
    submit=SubmitField('Register')

    def validate_username(self,username):
        if User.query.filter_by(username=username.data).first():
            raise ValidationError('Username already exists')
    
    def validate_email(self,email):
        if User.query.filter_by(email=email.data).first():
            raise ValidationError('Email already exists')
    


class CompanyRegistrationForm(FlaskForm):
    username=StringField('username',validators=[DataRequired(),Length(min=5,max=30)])
    Company_Name=StringField('Company Name',validators=[DataRequired()])
    website=StringField('website',validators=[DataRequired()])
    description=TextAreaField('description',validators=[DataRequired()])
    location=StringField('location',validators=[DataRequired()])
    email=StringField('email',validators=[DataRequired(),Email()])
    password=PasswordField('password',validators=[DataRequired()])
    confirm_password=PasswordField('confirm_password',validators=[DataRequired(),EqualTo('password')])
    submit=SubmitField('Register')

    def validate_username(self,username):
        if User.query.filter_by(username=username.data).first():
            raise ValidationError('Username already exists')
    def validate_email(self,email):
        if User.query.filter_by(email=email.data).first():
            raise ValidationError('Email already exists')

class LoginForm(FlaskForm):
    email=StringField('Email',validators=[DataRequired()])
    password=PasswordField('Password',validators=[DataRequired()])
    submit=SubmitField('Login')


class JobPostForm(FlaskForm):
    title=StringField('title',validators=[DataRequired()])
    description=TextAreaField('job description',validators=[DataRequired()])
    criteria=TextAreaField('Eligibility Criteria (e.g.,CGPA>7.0)',validators=[DataRequired()])
    salary=StringField('salary_package',validators=[DataRequired()])
    deadline=DateField('deadline',validators=[DataRequired()])
    submit=SubmitField('Post Placement Drive')

    def validate_deadline(self,deadline):
        if deadline.data < date.today():
            raise ValidationError('Deadline must be in the future')

