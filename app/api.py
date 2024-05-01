

import os
from flask import Blueprint, jsonify, request
from werkzeug.utils import secure_filename
from flask import current_app

from app import db
from app.models import Doc


api = Blueprint("api", __name__, url_prefix="/api")


@api.route("/docs", methods=["POST"])
def create_doc():
  data = request.form
  if not data or not data.get('title'):
    return 'Judul kosong', 400
  if not data or not data.get('year'):
    return 'Tahun kosong', 400
  if not data or not data.get('author'):
    return 'Penulis kosong', 400
  if not data or not data.get('classification'):
    return 'Klasifikasi kosong', 400
  if not data or not data.get('subject'):
    return 'Subjek kosong', 400
  if not data or not data.get('publisher'):
    return 'Penerbit kosong', 400
  if not data or not data.get('abstract'):
    return 'Abstrak kosong', 400
  if not data or not data.get('location'):
    return 'Lokasi kosong', 400
  
  title = request.form.get('title')
  year = request.form.get('year', type=int)  # Handle potential conversion errors
  author = request.form.get('author')
  classification = request.form.get('classification')
  subject = request.form.get('subject')
  publisher = request.form.get('publisher')
  abstract = request.form.get('abstract')
  location = request.form.get('location')
  new_doc = Doc(title=title, year=year, author=author, classification=classification,
                        subject=subject, publisher=publisher, abstract=abstract, location=location)

  try:
    db.session.add(new_doc)
    db.session.commit()
    return "Dokumen Berhasil Disimpan!", 201  # Created status code
  except Exception as e:
    db.session.rollback()
    return f"Error terjadi: {str(e)}", 500  # Internal Server Error

@api.route("/docs/batch", methods=['POST'])
def create_doc_batch():
  # jika file tidak kosong, masukkan ke database
  if secure_filename(request.files['file'].filename) != '':
    file = request.files['file']
    filename = secure_filename(file.filename)
    allowed_extension = ['xlsx', 'csv', 'xls']
    if filename.split('.')[-1].lower() not in allowed_extension:
      msg = 'Masukkan file dengan ekstensi xlsx, xls, atau csv'
      return msg, 400
    else:
      file.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))
      # TODO
      # baca excel tersebut kemudian jadikan pandas dataFrame
      # lalu cek apakah kolomnya sesuai 
      # colomns = ['title', 'year', 'author', 'classification', 'subject', 'publisher', 'abstract', 'location']
      # kalau tidak, kembalikan error
      # kalau sesuai, lakukan insert
      # buat tfidf vectorizer
      # lalu kembalikan success

      
      msg = 'File uploaded successfully'
      return msg, 201
  else:
    msg = 'File kosong'
    return msg, 400
  
  

@api.route("/docs/<int:id>")
def get_doc(id):
  doc = Doc.query.get_or_404(id)
  return doc.to_json()
  # try:
  # except Exception as e:
  #   db.session.rollback()
  #   return f"An error occurred: {str(e)}", 500  # Internal Server Error
  
@api.route("/docs/<int:id>", methods=["PUT"])
def update_doc(id):
  doc = Doc.query.get_or_404(id)

  doc.title = request.form.get('title')
  doc.year = request.form.get('year', type=int)  # Handle potential conversion errors
  doc.author = request.form.get('author')
  doc.classification = request.form.get('classification')
  doc.subject = request.form.get('subject')
  doc.publisher = request.form.get('publisher')
  doc.abstract = request.form.get('abstract')
  doc.location = request.form.get('location')
  db.session.commit()
  return doc.to_json(), 200 # Created status code
  
@api.route("/docs/<int:id>", methods=["DELETE"])
def delete_doc(id):
  doc = Doc.query.get_or_404(id)
  
  try:
    db.session.delete(doc)
    db.session.commit()
    return "Doc deleted successfully!", 200  # Created status code
  except Exception as e:
    db.session.rollback()
    return f"An error occurred: {str(e)}", 500  # Internal Server Error
