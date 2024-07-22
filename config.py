import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
  SECRET_KEY = os.environ.get('SECRET_KEY') or 'default-very-secret-key'
  # SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'mysql://root:@localhost/db_opac' 
  SQLALCHEMY_DATABASE_URI = f"mysql+mysqldb://{os.getenv('MYSQL_USER')}:{os.getenv('MYSQL_PASSWORD')}@{os.getenv('MYSQL_HOST')}/{os.getenv('MYSQL_DB')}"
  SQLALCHEMY_TRACK_MODIFICATIONS = False

  UPLOAD_FOLDER = 'app/static/uploads'
  W2V_MODEL = 'we_model\idwiki_new_lower_word2vec_200\idwiki_new_lower_word2vec_200.model'
  W2V_MODEL_SG = 'we_model\idwiki_new_lower_word2vec_300\idwiki_new_lower_word2vec_300.model'
  # SECRET_KEY = os.environ.get('SECRET_KEY') or 'default-very-secret-key'