from flask import Blueprint, render_template,redirect,url_for,flash,request,make_response
from .form import StudentRegistrationForm,CompanyRegistrationForm,LoginForm,JobPostForm
from werkzeug.security import generate_password_hash,check_password_hash,check_password_hash
from .models import db,User,Student,Company,Job,Applications
from flask_login import login_user,login_required,logout_user,current_user
from datetime import datetime
from sqlalchemy import or_
import csv
import io

main=Blueprint('main',__name__)

@main.route('/')
def index():
    
    if current_user.is_authenticated:
        if current_user.role == 'admin':
            return redirect(url_for('main.admin_dashboard'))
        elif current_user.role == 'company':
            return redirect(url_for('main.company_dashboard'))
        else:
            return redirect(url_for('main.student_dashboard'))
            
    
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
    
@main.route('/student_dashboard')
@login_required
def student_dashboard():
    if current_user.role != 'student':
        flash('Access denied.', 'danger')
        return redirect(url_for('main.login'))

    today = datetime.utcnow()
    
   
    my_applications = Applications.query.filter_by(student_id=current_user.student_profile.id).all()
    applied_job_ids = [app.job_id for app in my_applications]
    
    
    pending_apps = [app for app in my_applications if app.status == 'Applied']
    processed_apps = [app for app in my_applications if app.status in ['Shortlisted', 'Selected', 'Rejected']]

    available_jobs = Job.query.filter(
        Job.status == 'Approved',
        Job.deadline >= today,
        ~Job.id.in_(applied_job_ids) if applied_job_ids else True 
    ).all()

    return render_template('student_dashboard.html', 
                           jobs=available_jobs, 
                           pending_apps=pending_apps,
                           processed_apps=processed_apps)

@main.route('/student/apply/<int:job_id>',methods=['POST'])
@login_required
def apply_job(job_id):
    if current_user.role!= 'student':
        flash('You are not authorized to access this page','danger')
        return redirect(url_for('main.login'))
    
    job=Job.query.get_or_404(job_id)
    if job.status !='Approved':
        flash('You cannot apply to this job.','danger')
        return redirect(url_for('main.student_dashboard'))
    
    if job.deadline <datetime.utcnow():
        flash('You cannot apply to this job.','danger')
        return redirect(url_for('main.student_dashboard'))
    
    existing_app=Applications.query.filter_by(
        student_id=current_user.student_profile.id,
        job_id=job.id
    ).first()

    if existing_app:
        flash('You have already applied to this job','warning')
        return redirect(url_for('main.student_dashboard'))
    else:
        new_app=Applications(
            student_id=current_user.student_profile.id,
            job_id=job.id,
            status='Applied'
        )
        db.session.add(new_app)
        db.session.commit()
        flash(f'You have successfully applied for {job.title} at {job.company.company_name}','success')
        return redirect(url_for('main.student_dashboard'))

@main.route('/student/edit_profile',methods=['GET','POST'])
@login_required
def edit_student_profile():
    if current_user.role!='student':
        return redirect(url_for('main.login'))
    
    student=current_user.student_profile
    
    if request.method=='POST':
        student.name=request.form.get('full_name')
        student.cgpa=float(request.form.get('cgpa'))
        student.resume_url=request.form.get('resume_url')
        db.session.commit()
        flash('Profile updated successfully','success')
        return redirect(url_for('main.student_dashboard'))
    
    return render_template('edit_student_profile.html',student=student)
    

@main.route('/company_dashboard')
@login_required
def company_dashboard():
    if current_user.role != 'company':
        return redirect(url_for('main.login'))
    if not current_user.company_profile.is_approved:
        flash('Your account is pending approval.', 'warning')
        return redirect(url_for('main.login'))

    
    today = datetime.utcnow()
    all_my_jobs = Job.query.filter_by(company_id=current_user.company_profile.id).order_by(Job.deadline.desc()).all()
    
    ongoing_drives = []
    closed_drives = []
    
    for job in all_my_jobs:
      
        if job.status in ['Closed', 'Completed', 'Rejected'] or (job.status == 'Approved' and job.deadline < today):
            closed_drives.append(job)
        else:
            ongoing_drives.append(job)
            
    return render_template('company_dashboard.html', 
                           ongoing_drives=ongoing_drives, 
                           closed_drives=closed_drives, 
                           today=today) 

@main.route('/company/job/<int:job_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_job(job_id):
    if current_user.role != 'company':
        return redirect(url_for('main.login'))
        
    job = Job.query.get_or_404(job_id)
    
    
    if job.company_id != current_user.company_profile.id:
        flash('Unauthorized action.', 'danger')
        return redirect(url_for('main.company_dashboard'))

    if job.status == 'Closed' or job.deadline < datetime.utcnow():
        flash('Cannot edit a closed or expired drive.', 'warning')
        return redirect(url_for('main.company_dashboard'))

    form = JobPostForm(obj=job) 
    
    if form.validate_on_submit():
        job.title = form.title.data
        job.description = form.description.data
        job.eligibility_criteria = form.criteria.data
        job.salary = form.salary.data
        job.deadline = form.deadline.data
        db.session.commit()
        flash('Placement Drive updated successfully!', 'success')
        return redirect(url_for('main.company_dashboard'))
        
    return render_template('create_job.html', form=form, edit_mode=True) 

@main.route('/company/job/<int:job_id>/close')
@login_required
def close_company_job(job_id):
    if current_user.role != 'company':
        return redirect(url_for('main.login'))
        
    job = Job.query.get_or_404(job_id)
    if job.company_id == current_user.company_profile.id:
        job.status = 'Closed'
        db.session.commit()
        flash(f'Drive "{job.title}" has been marked as completed/closed.', 'info')
        
    return redirect(url_for('main.company_dashboard'))

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

@main.route('/company/job/<int:job_id>/applications')
@login_required
def view_applications(job_id):
    if current_user.role!='company':
        flash('You are not authorized to access this page','danger')
        return redirect(url_for('main.login'))
    
    job=Job.query.get_or_404(job_id)
    if job.company_id!=current_user.company_profile.id:
        flash('You are not authorized to access this page','danger')
        return redirect(url_for('main.company_dashboard'))

    applications=Applications.query.filter_by(job_id=job.id).all()

    return render_template('job_applications.html',job=job,applications=applications)

@main.route('/company/application/<int:app_id>/update',methods=['POST'])
@login_required
def update_application_status(app_id):
    if current_user.role !='company':
        return redirect(url_for('main.login'))
    application=Applications.query.get_or_404(app_id)

    if application.job.company_id!=current_user.company_profile.id:
        flash('Unauthorized action.','danger')
        return redirect(url_for('main.company_dashboard'))
    
    new_status=request.form.get('status')
    if new_status in ['Applied', 'Shortlisted', 'Selected', 'Rejected']:
        application.status=new_status
        db.session.commit()
        flash(f"Application status for {application.student.name} updated to {new_status}.",'success')
    
    return redirect(url_for('main.view_applications',job_id=application.job.id))


@main.route('/admin/dashboard')
@login_required
def admin_dashboard():
    if current_user.role!='admin':
        flash('You are not authorized to access this page','danger')
        return redirect(url_for('main.index'))

    
    all_students=Student.query.all()
    approved_companies=Company.query.filter_by(is_approved=True).all()

    total_students=Student.query.count()
    total_companies=Company.query.count()
    total_drives=Job.query.count()
    total_applications=Applications.query.count()

    pending_companies=Company.query.filter_by(is_approved=False).all()
    pending_jobs=Job.query.filter_by(status='Pending').all()

    ongoing_jobs=Job.query.filter_by(status='Approved').all()
    all_applications=Applications.query.order_by(Applications.date_applied.desc()).all()

    

    return render_template('admin_dashboard.html',t_students=total_students,t_companies=total_companies,
    t_drives=total_drives,t_applications=total_applications,pending_companies=pending_companies,
    approved_companies=approved_companies,all_students=all_students,pending_jobs=pending_jobs,
    ongoing_jobs=ongoing_jobs,all_applications=all_applications)

@main.route('/admin/search')
@login_required
def admin_search():
    if current_user.role != 'admin':
        return redirect(url_for('main.login'))
        
    search_query = request.args.get('search', '').strip()
    
    
    if not search_query:
        return redirect(url_for('main.admin_dashboard'))

    
    found_students = Student.query.join(User).filter(
        db.or_(
            Student.name.ilike(f'%{search_query}%'),
            Student.id == (int(search_query) if search_query.isdigit() else 0),
            User.email.ilike(f'%{search_query}%')
        )
    ).all()
    
    
    found_companies = Company.query.filter(
        Company.is_approved == True,
        Company.company_name.ilike(f'%{search_query}%')
    ).all()

    return render_template('search_results.html', 
                           query=search_query, 
                           students=found_students, 
                           companies=found_companies)


@main.route('/admin/view_detail/<string:role>/<int:profile_id>')
@login_required
def view_detail(role,profile_id):
    if current_user.role!='admin':
        return redirect(url_for('main.login'))
    
    profile=None
    if role=='student':
        profile=Student.query.get_or_404(profile_id)
    elif role=='company':
        profile=Company.query.get_or_404(profile_id)
    
    return render_template('view_detail.html',profile=profile,role=role)

@main.route('/admin/mark_drive_complete/<int:job_id>')
@login_required
def mark_drive_complete(job_id):
    if current_user.role!='admin':
        return redirect(url_for('main.login'))
    
    job=Job.query.get_or_404(job_id)
    job.status='Completed'
    db.session.commit()
    flash(f'Placement Drive "{job.title}" has been marked as complete!', 'success')
    return redirect(url_for('main.admin_dashboard'))


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

@main.route('/admin/export_applications')
@login_required
def export_applications():
    if current_user.role != 'admin':
        return redirect(url_for('main.login'))
    applications=Applications.query.all()

    si=io.StringIO()
    cw=csv.writer(si)

    cw.writerow(['App ID', 'Student Name', 'Student Email', 'Student CGPA', 'Company Name', 'Job Title', 'Date Applied', 'Final Status'])

    for app in applications:
        cw.writerow([
            app.id,
            app.student.name,
            app.student.user.email,
            app.student.cgpa,
            app.job.company.company_name,
            app.job.title,
            app.date_applied,
            app.status
        ])
    
    output=make_response(si.getvalue())

    output.headers['content-Disposition']='attachment; filename="placement_applications.csv"'

    return output







@main.route('/logout')
def logout():

    logout_user()
    flash('You have been logged out','success')
    return redirect(url_for('main.index'))
