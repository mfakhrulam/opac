import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
  SECRET_KEY = os.environ.get('SECRET_KEY') or 'default-very-secret-key'
  SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'mysql://root:@localhost/db_opac' 
  UPLOAD_FOLDER = 'app/static/uploads'
  W2V_MODEL = 'we_model\idwiki_new_lower_word2vec_200\idwiki_new_lower_word2vec_200.model'
  W2V_MODEL_SG = 'we_model\idwiki_new_lower_word2vec_300\idwiki_new_lower_word2vec_300.model'
  # SECRET_KEY = os.environ.get('SECRET_KEY') or 'default-very-secret-key'