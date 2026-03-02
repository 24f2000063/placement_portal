from flask import Blueprint, render_template,redirect,url_for,flash
from .form import StudentRegistrationForm,CompanyRegistrationForm,LoginForm,JobPostForm
from werkzeug.security import generate_password_hash,check_password_hash,check_password_hash
from .models import db,User,Student,Company,Job,Applications
from flask_login import login_user,login_required,logout_user,current_user

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

            if user.is_blocked:
                flash('Your account has been blocked.please contact support team','danger')
                return redirect(url_for('main.login'))


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
    if current_user.role!='company':
        flash('You are not authorized to access this page','danger')
        return redirect(url_for('main.login'))
    
    if not current_user.company_profile.is_approved:
        flash('Your company profile is not approved yet','warning')
        return redirect(url_for('main.login'))

    my_jobs=Job.query.filter_by(company_id=current_user.company_profile.id)

    return render_template('company_dashboard.html',jobs=my_jobs)


@main.route('/company/create_job',methods=['GET','POST'])
@login_required
def create_job():
    if current_user.role!='company':
        flash('You are not authorized to access to access this page','danger')
        return redirect(url_for('main.login'))
    form=JobPostForm()
    if form.validate_on_submit():
        job=Job(
            title=form.title.data,
            description=form.description.data,
            requirements=form.criteria.data,
            salary=form.salary.data,
            deadline=form.deadline.data,
            company_id=current_user.company_profile.id,
            status='Pending'
        )
        db.session.add(job)
        db.session.commit()
        flash('Job posted successfully','success')
        return redirect(url_for('main.company_dashboard'))
    return render_template('create_job.html',form=form)

@main.route('/admin/dashboard')
@login_required
def admin_dashboard():
    if current_user.role!='admin':
        flash('You are not authorized to access this page','danger')
        return redirect(url_for('main.index'))

    total_students=Student.query.count()
    total_companies=Company.query.count()
    total_drives=Job.query.count()
    total_applications=Applications.query.count()

    pending_companies=Company.query.filter_by(is_approved=False).all()
    approved_companies=Company.query.filter_by(is_approved=True).all()

    all_students=Student.query.all()
    pending_jobs=Job.query.filter_by(status='Pending').all()

    return render_template('admin_dashboard.html',t_students=total_students,t_companies=total_companies,
    t_drives=total_drives,t_applications=total_applications,pending_companies=pending_companies,
    approved_companies=approved_companies,all_students=all_students,pending_jobs=pending_jobs)

@main.route('/admin/approve_job/<int:job_id>')
@login_required
def approve_job(job_id):
    if current_user.role!='admin':
        flash('You are not authorized to access this page','danger')
        return redirect(url_for('main.login'))

    job=Job.query.get_or_404(job_id)
    job.status='Approved'
    db.session.commit()
    flash(f'Placement Drive "{job.title}" has been approved!', 'success')
    return redirect(url_for('main.admin_dashboard'))

@main.route('/admin/reject_job/<int:job_id>')
@login_required
def reject_job(job_id):
    if current_user.role!='admin':
        flash('You are not authorized to access this page','danger')
        return redirect(url_for('main.login'))
    
    job=Job.query.get_or_404(job_id)
    job.status='Rejected'
    db.session.commit()
    flash(f'Placement Drive "{job.title}" has been rejected!', 'success')
    return redirect(url_for('main.admin_dashboard'))

@main.route('/admin/approve_company/<int:company_id>')
@login_required
def approve_company(company_id):
    if current_user.role!='admin':
        flash('You are not authorized to access this page','danger')
        return redirect(url_for('main.login'))
    
    company=Company.query.get_or_404(company_id)
    company.is_approved=True
    db.session.commit()
    flash(f'Company {company.company_name} approved successfully','success')
    return redirect(url_for('main.admin_dashboard'))

@main.route('/admin/reject_company/<int:company_id>')
@login_required
def reject_company(company_id):
    if current_user.role!='admin':
        flash('You are not authorized to access this page','danger')
        return redirect(url_for('main.login'))
    
    company=Company.query.get_or_404(company_id)
    user=User.query.get(company.user_id)
    db.session.delete(user)
    db.session.delete(company)
    db.session.commit()
    flash(f'Company {company.company_name} rejected and removed successfully','success')
    return redirect(url_for('main.admin_dashboard'))


@main.route('/admin/toggle_blacklist/<int:user_id>')
@login_required
def toggle_blacklist(user_id):
    if current_user.role!='admin':
        flash('You are not authorized to access this page','danger')
        return redirect(url_for('main.login'))

    
    user=User.query.get_or_404(user_id)

    if user.is_blocked:
        user.is_blocked=False
        flash(f'User {user.username} unblocked successfully','success')
    else:
        user.is_blocked=True
        flash(f'User {user.username} blocked successfully ','danger')

    db.session.commit()
    return redirect(url_for('main.admin_dashboard'))







@main.route('/logout')
def logout():
    logout_user()
    flash('You have been logged out','success')
    return redirect(url_for('main.index'))
