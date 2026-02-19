from flask_wtf import FlaskForm
from wtforms import StringField,PasswordField,FloatField,SubmitField,TextAreaField
from wtforms.validators import DataRequired,Length,Email,EqualTo,URL,ValidationError
from .models import User
class StudentRegistrationForm(FlaskForm):
    username = StringField('username', validators=[DataRequired(),Length(min=2,max=20)])
    name=StringField('name',validators=[DataRequired()])
    email=StringField('email',validators=[DataRequired(),Email()])
    password=PasswordField('password',validators=[DataRequired()])
    confirm_password=PasswordField('confirm_password',validators=[DataRequired(),EqualTo('password')])
    cgpa=FloatField('cgpa',validators=[DataRequired()])
    branch=StringField('branch',validators=[DataRequired()])
    roll_no=StringField('roll_no',validators=[DataRequired()])
    resume_url=StringField('resume_url',validators=[DataRequired(),URL(message="Please enter a valid URL.")])
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