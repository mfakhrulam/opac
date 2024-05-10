import os
from flask import Blueprint, request
import openpyxl
from werkzeug.utils import secure_filename
from flask import current_app
import time


from app import db
from app.models import Doc

import pandas as pd

from .api_utils import build_index, check_different_column_names, from_df_to_database

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
    # build index
    build_index()
    return "Dokumen Berhasil Disimpan!", 201 
  except Exception as e:
    db.session.rollback()
    return f"Error terjadi: {str(e)}", 500  

@api.route("/docs/batch", methods=['POST'])
def create_doc_batch():
  # jika file tidak kosong, masuk ke logic
  if secure_filename(request.files['file'].filename) != '':
    file = request.files['file']
    filename = secure_filename(file.filename)
    allowed_extension = ['xlsx', 'csv']
    
    # jika ekstensi tidak sesuai maka return, jika tidak, masuk ke logic
    if filename.split('.')[-1].lower() not in allowed_extension:
      # return jsonify({
      #   'status': 'error',
      #   'message': 'Masukkan file dengan ekstensi xlsx, xls, atau csv'
      #   }), 400
      return 'Masukkan file dengan ekstensi xlsx atau csv', 400
    else:
      file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
      file.save(file_path)
      
      # baca dan cek apakah kolomnya sesuai 
      if filename.split('.')[-1].lower() == 'xlsx':
        df = pd.read_excel(file_path)
      else:
        df = pd.read_csv(file_path)
      
      try:
        expected_columns = ['title', 'year', 'author', 'classification', 'subject', 'publisher', 'abstract', 'location']
        df = df[expected_columns]
        df =df.fillna('null')

        
      except Exception as e:
        os.remove(file_path)
        return 'Kolom tidak sesuai: ' + str(e), 400
      
      # expected_columns = ['title', 'year', 'author', 'classification', 'subject', 'publisher', 'abstract', 'location']
      # different_columns_names = check_different_column_names(df, expected_columns)
      
      # # kalau tidak sesuai / ada yang beda, kembalikan error
      # if different_columns_names:
      #   os.remove(file_path)
      #   # return jsonify({
      #   #   'status': 'error',
      #   #   'message': 'Kolom tidak sesuai: ' + str(different_columns_names)
      #   # }), 400
      #   return 'Kolom tidak sesuai: ' + str(different_columns_names), 400
      
      # kalau sesuai, lakukan insert
      df['abstract'] = df['abstract'].astype(str).apply(openpyxl.utils.escape.unescape)
      try:
        from_df_to_database(df)
      except Exception as e:
        # msg = {
        #   'status': 'error',
        #   'message': e
        # }
        return str(e), 500

      start_time = time.time()
      # build index
      build_index()
      print("--- %s seconds ---" % (time.time() - start_time))
      # lalu kembalikan success
      # msg = {
      #   'status': 'success',
      #   'message': 'File uploaded successfully'
      # }
      # return jsonify(msg), 201
      return 'Dokumen sukses diupload', 201
  else:
    return 'File kosong', 400
  
  

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
  update_index = False
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
  
  if doc.title != request.form.get('title') or doc.subject != request.form.get('subject') or doc.abstract != request.form.get('abstract'):
    update_index = True
  
  doc.title = request.form.get('title')
  doc.year = request.form.get('year', type=int)  # Handle potential conversion errors
  doc.author = request.form.get('author')
  doc.classification = request.form.get('classification')
  doc.subject = request.form.get('subject')
  doc.publisher = request.form.get('publisher')
  doc.abstract = request.form.get('abstract')
  doc.location = request.form.get('location')

  try:
    db.session.commit()
    # build index
    if update_index:
      start_time = time.time()
      build_index()
      print("--- %s seconds ---" % (time.time() - start_time))
    return "Dokumen Berhasil Disimpan!", 201 
  except Exception as e:
    db.session.rollback()
    return f"Error terjadi: {str(e)}", 500  
  
@api.route("/docs/<int:id>", methods=["DELETE"])
def delete_doc(id):
  doc = Doc.query.get_or_404(id)
  
  try:
    db.session.delete(doc)
    db.session.commit()
    # build index
    start_time = time.time()
    build_index()
    print("--- %s seconds ---" % (time.time() - start_time))
    return "Dokumen Berhasil Dihapus!", 200  # Created status code
  except Exception as e:
    db.session.rollback()
    return f"Error terjadi: {str(e)}", 500  # Internal Server Error
