from flask import Blueprint, render_template,redirect,url_for,flash
from .form import StudentRegistrationForm,CompanyRegistrationForm,LoginForm
from werkzeug.security import generate_password_hash,check_password_hash,check_password_hash
from .models import db,User,Student,Company
from flask_login import login_user,login_required,logout_user

main=Blueprint('main',__name__)

@main.route('/')
def index():
    return render_template('home.html')

@main.route('/register/<role>',methods=['GET','POST'])
def register(role):
    if role=='student':
        form=StudentRegistrationForm()
    elif role=='company':
        form=CompanyRegistrationForm()   
    
    if form.validate_on_submit():
        hashed_password=generate_password_hash(form.password.data)
        new_user=User(username=form.username.data,email=form.email.data,password=hashed_password,role=role)
        db.session.add(new_user)
        db.session.flush()

        if role=='student':
            new_profile=Student(
                user_id=new_user.id,
                name=form.name.data,
                roll_no=form.roll_no.data,
                branch=form.branch.data,
                cgpa=form.cgpa.data,
                resume_url=form.resume_url.data,

            )
        else:
            new_profile=Company(
                user_id=new_user.id,
                company_name=form.Company_Name.data,
                website=form.website.data,
                description=form.description.data,
                location=form.location.data,

            )
        db.session.add(new_profile)
        db.session.commit()
        flash('Registration successful','success')
        return redirect(url_for('main.login'))
    return render_template('register.html',form=form,role=role)


@main.route('/login',methods=['GET','POST'])
def login():
    form=LoginForm()
    if form.validate_on_submit():
        user=User.query.filter_by(email=form.email.data).first()
        if user and check_password_hash(user.password, form.password.data):
            if user.role=='company' and not user.company_profile.is_approved:
                flash('Your company profile is not approved yet','warning')
                return redirect(url_for('main.index'))
            
            login_user(user)
            flash(f'Welcome back {user.username}!','success')

            if user.role=='student':
                return redirect(url_for('main.student_dashboard'))
            elif user.role=='company':
                return redirect(url_for('main.company_dashboard'))
            else:
                return redirect(url_for('main.admin_dashboard'))
        else:
            flash('Invalid email or password','danger')
    
    return render_template('login.html',form=form)
    
@main.route('/student/dashboard')
@login_required
def student_dashboard():
    return "<h1>Student Dashboard</h1>"

@main.route('/company/dashboard')
@login_required
def company_dashboard():
    return "<h1>Company Dashboard</h1>"

@main.route('/admin/dashboard')
@login_required
def admin_dashboard():
    return "<h1>Admin Dashboard</h1>"

@main.route('/logout')
def logout():
    logout_user()
    flash('You have been logged out','success')
    return redirect(url_for('main.index'))
