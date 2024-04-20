from typing import Optional
from datetime import datetime
import sqlalchemy as sa
import sqlalchemy.orm as so
from app import db

from werkzeug.security import generate_password_hash, check_password_hash

class User(db.Model):
  id: so.Mapped[int] = so.mapped_column(primary_key=True)
  username: so.Mapped[str] = so.mapped_column(sa.String(64), index=True, unique=True)
  password_hash: so.Mapped[Optional[str]] = so.mapped_column(sa.String(256))

  def set_password(self, password):
    self.password_hash = generate_password_hash(password)

  def check_password(self, password):
    return check_password_hash(self.password_hash, password)

  def __repr__(self):
    return '<User {}>'.format(self.username)
  
class Docs(db.Model):
  id: so.Mapped[int] = so.mapped_column(primary_key=True)
  title: so.Mapped[str] = so.mapped_column(sa.String(255), index=True)
  year: so.Mapped[int] = so.mapped_column()
  author: so.Mapped[str] = so.mapped_column(sa.String(255))
  classification: so.Mapped[str] = so.mapped_column(sa.String(255))
  publisher: so.Mapped[str] = so.mapped_column(sa.String(255))
  abstract: so.Mapped[str] = so.mapped_column(sa.Text)
  location: so.Mapped[str] = so.mapped_column(sa.String(255))
  created_at: so.Mapped[datetime] = so.mapped_column(insert_default=sa.func.now())
  updated_at: so.Mapped[Optional[datetime]] = so.mapped_column(nullable=True)
  
  def __repr__(self):
    return '<Docs {}>'.format(self.title)
