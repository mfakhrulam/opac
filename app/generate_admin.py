from app.models import User
from app import db

admin = User(username="admin")
admin.set_password("admin")
db.session.add(admin)
db.session.commit()