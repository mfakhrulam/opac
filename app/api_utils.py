from config import Config
from sqlalchemy import create_engine
import os
import pickle
import pandas as pd
from app.models import Doc
from app import db
from helper import wordList_preprocessing
from sklearn.feature_extraction.text import TfidfVectorizer


def check_different_column_names(df, column_names_list):
  """
  Checks if all column names in the DataFrame match the provided list and returns
  a list of different column names (if any).

  Args:
      df (pd.DataFrame): The DataFrame to check.
      column_names_list (list): The list of expected column names.

  Returns:
      list: A list containing the different column names (empty list if all match).
  """

  # Convert both to sets for efficient comparison
  df_columns_set = set([col.lower() for col in df.columns])
  expected_columns_set = set(column_names_list)

  # Find the difference between sets to get different column names
  different_columns = df_columns_set.difference(expected_columns_set)

  return list(different_columns)  # Convert set back to list for output

def from_df_to_database(df):
  # ini nanti diganti, jadi hanya fokus untuk df ke database
  # logic mengenai pengecekan column dimasukkan ke main 
  # programnya aja. termasuk untuk mengganti escape character
  # atau yang lainnya di bagian abstract di situ.
  engine = create_engine(Config.SQLALCHEMY_DATABASE_URI)
  # df = pd.read_excel('file_path')
  # df['abstract'] = df['abstract'].astype(str).apply(openpyxl.utils.escape.unescape)
  
  with engine.begin() as connection:
    df.to_sql(
      name='docs',
      con=connection,
      if_exists='append',
      index=False,
    )

def build_index():
  # ambil semua data dari database, ambil colomn yang digu=nakan
  df = pd.read_sql(db.session.query(Doc).statement, db.session.connection())
  # ambil ‘title’ atau judul dan jadikan sebagai dictionary
  input_title_only = df['title']
  # input_title_subject_abstract = df['title'] + '. ' + df['subject'] + '. '+ df['abstract']
  # input_title_subject = df['title'] + '. ' + df['subject']
  docs = input_title_only.to_dict()
  # preproses data judul
  docs, _ = wordList_preprocessing(docs)
  # inisialisasi TfidfVectorizer dan bentuk kosa kata berdasarkan data judul di atas
  tfidf_vectorizer = TfidfVectorizer(norm=None, sublinear_tf=False)
  # transformasikan setiap kata dari judul dan buat matrix tf-idf
  tfidf_vectorizer.fit(docs.values()) # This determines the vocabulary.
  tf_idf_sparse = tfidf_vectorizer.transform(docs.values())
  # simpan vectorizer dan matrix tfidf
  with open('pickle_model/tfidf_vectorizer.pkl', 'wb') as file:
    pickle.dump(tfidf_vectorizer, file)
  with open('pickle_model/tfidf_sparse.pkl', 'wb') as file:
    pickle.dump(tf_idf_sparse, file)
  
def read_index():
  with open('pickle_model/tfidf_vectorizer.pkl', 'rb') as file:
    tfidf_vectorizer = pickle.load(file)
  with open('pickle_model/tfidf_sparse.pkl', 'rb') as file:
    tf_idf_sparse = pickle.load(file)
  return tfidf_vectorizer, tf_idf_sparse