import pandas as pd
import pickle
from sklearn.feature_extraction.text import TfidfVectorizer
import pandas as pd
import openpyxl
from config import Config
from sqlalchemy import create_engine
from app import app, db


def get_list_docs(input_data='title_only'):  
  """
  Reads a CSV file containing document information and returns a list of document titles based on the input_data parameter.
  
  Parameters:
    input_data (str, optional): The type of data to return. Defaults to 'title_only'.
      - 'title_only': Returns a list of document titles.
      - 'title_subject': Returns a list of document titles followed by their subjects.
      - 'title_subject_abstract': Returns a list of document titles followed by their subjects and abstracts.
  
  Returns:
    pandas.Series or None: A Series of document titles if input_data is 'title_only'.
    pandas.Series or None: A Series of document titles followed by their subjects if input_data is 'title_subject'.
    pandas.Series or None: A Series of document titles followed by their subjects and abstracts if input_data is 'title_subject_abstract'.
    None: If input_data is not one of the specified options.
  """
  df = pd.read_csv("./dataset/data_scrapping_opac_page_313 (1).csv")
  df = df[df['year'] != 2024].reset_index(drop=True)
  if input_data == 'title_only':
    return df['title']
  elif input_data == 'title_subject':
    return df['title'] + '. ' + df['subject']
  elif input_data == 'title_subject_abstract':
    return df['title'] + '. ' + df['subject'] + '. '+ df['abstract']
  else:
    return None 

def create_vectorizer_sparse(docs, vectorizer_path, sparse_path):
  """
  Create a vectorizer and transform the documents to sparse matrix.
  This function is used to reindex the data if there are updates in the dataset.

  Parameters:
    docs (pandas.Series): A Series of document titles.

  """
  tfidf_vectorizer = TfidfVectorizer(norm=None, sublinear_tf=False) # Do not normalize.
  tfidf_vectorizer.fit(docs.values()) # This determines the vocabulary.
  tf_idf_sparse = tfidf_vectorizer.transform(docs.values())
  
  # Save the vectorizer to a pickle file.
  with open(vectorizer_path, 'wb') as file:
    pickle.dump(tfidf_vectorizer, file)
  
  # Save the sparse matrix to a pickle file.
  with open(sparse_path, 'wb') as file:
    pickle.dump(tf_idf_sparse, file)

def load_vectorizer_sparse(vectorizer_path, sparse_path):
  vectorizer = pickle.load(open(vectorizer_path,'rb'))
  sparse = pickle.load(open(sparse_path,'rb'))
  return vectorizer, sparse

def from_df_to_database(df, file_path):
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

# df = pd.read_excel('dataset\egdata.xlsx')
# df['abstract'] = df['abstract'].astype(str).apply(openpyxl.utils.escape.unescape)
# engine = create_engine(Config.SQLALCHEMY_DATABASE_URI)

# with engine.begin() as connection:
#   df.to_sql(
#     name='docs',
#     con=connection,
#     if_exists='append',
#     index=False,
#   )

def from_database_to_df(query, columns):
  df = pd.read_sql(query.statement, query.bind, columns=columns)
  return df