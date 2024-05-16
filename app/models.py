from typing import Optional
from datetime import datetime
import sqlalchemy as sa
import sqlalchemy.orm as so
from app import db
from app import login

from flask_login import UserMixin

from werkzeug.security import generate_password_hash, check_password_hash

class User(UserMixin, db.Model):
  __tablename__ = 'users'
  id: so.Mapped[int] = so.mapped_column(primary_key=True)
  username: so.Mapped[str] = so.mapped_column(sa.String(64), index=True, unique=True)
  password_hash: so.Mapped[Optional[str]] = so.mapped_column(sa.String(256))

  def set_password(self, password):
    self.password_hash = generate_password_hash(password)

  def check_password(self, password):
    return check_password_hash(self.password_hash, password)

  def __repr__(self):
    return '<User {}>'.format(self.username)
  
@login.user_loader
def load_user(id):
  return User.query.get(id)
  
class Doc(db.Model):
  __tablename__ = 'docs'
  id: so.Mapped[int] = so.mapped_column(primary_key=True)
  title: so.Mapped[str] = so.mapped_column(sa.String(255), index=True)
  year: so.Mapped[int] = so.mapped_column()
  author: so.Mapped[str] = so.mapped_column(sa.String(255))
  classification: so.Mapped[str] = so.mapped_column(sa.String(255))
  subject: so.Mapped[str] = so.mapped_column(sa.String(255))
  publisher: so.Mapped[str] = so.mapped_column(sa.String(255))
  abstract: so.Mapped[str] = so.mapped_column(sa.Text)
  location: so.Mapped[str] = so.mapped_column(sa.String(255))
  created_at: so.Mapped[datetime] = so.mapped_column(insert_default=sa.func.now(), server_default=sa.text('CURRENT_TIMESTAMP'))
  updated_at: so.Mapped[Optional[datetime]] = so.mapped_column(nullable=True, onupdate=sa.func.now())
  
  def get_paginated_docs(page, per_page=20):
    page = db.paginate(db.select(Doc).order_by(Doc.id.desc()), page=page, per_page=per_page)
    return page
  
  def to_json(self):
    return {
      'id': self.id,
      'title': self.title,
      'year': self.year,
      'author': self.author,
      'classification': self.classification,
      'subject': self.subject,
      'publisher': self.publisher,
      'abstract': self.abstract,
      'location': self.location,
      'created_at': self.created_at,
      'updated_at': self.updated_at
    }
  
  def __repr__(self):
    return '<Docs {} - {}>'.format(self.id, self.title)
