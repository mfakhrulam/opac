from app import db
from app.models import User

def init_db():
    db.create_all()

    # Tambahkan admin
    admin = User(username='admin')
    admin.set_password('admin123#')
    db.session.add(admin)
    db.session.commit()

if __name__ == '__main__':
    init_db()
