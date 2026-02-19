from app import create_app,db
from app.models import User
from werkzeug.security import generate_password_hash
app=create_app()

with app.app_context():

    admin=User.query.filter_by(role='admin').first()
    if not admin:
        hashed_password=generate_password_hash('admin123')
        new_admin=User(username='admin',email='admin@iitm.ac.in',password=hashed_password,role='admin')
        db.session.add(new_admin)
        db.session.commit()
        print('Admin created successfully')
    else:
        print('Admin already exists')

