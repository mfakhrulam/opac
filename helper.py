from collections import Counter, OrderedDict
import math
import re

from copy import deepcopy
import numpy as np  

from Sastrawi.StopWordRemover.StopWordRemoverFactory import StopWordRemoverFactory
from Sastrawi.Stemmer.StemmerFactory import StemmerFactory

import nltk
from nltk import word_tokenize
from nltk.tokenize.regexp import regexp_tokenize

from gensim.models import KeyedVectors

def preprocessing(text):
  """
  Melakukan pra-pemrosesan teks dengan langkah-langkah berikut:
      - Mengubah huruf menjadi huruf kecil.
      - Mengganti baris baru, kembali ke garis, dan tab dengan spasi.
      - Mengganti angka dan tanda baca (kecuali kutip tunggal) dengan spasi.
      - Menghapus tanda kutip tunggal.
      - Menghapus karakter selain huruf, angka, dan spasi.
      - Menghapus spasi berlebih.
  
  Parameter:
      text (str): Teks yang akan diproses.
  
  Returns:
      str: Teks yang telah diproses.
    """
  # case folding
  text = text.lower()
  # replace new line, carriage return, and tab with white space,
  text = text.replace("\r", " ").replace("\n", " ").replace("\t", " ")
  # replace number, punctuations (except single quote) with space
  punc_list = '!"#$%&()*+,-./:;<=>?@[\]^_`{|}~' + '0123456789'
  text = text.translate(str.maketrans(dict.fromkeys(punc_list, " ")))
  # replace single quote with empty string
  text = text.translate(str.maketrans(dict.fromkeys("'`", "")))
  text = re.sub(r"[^a-zA-Z0-9\s]", "", text)

  # remove extra whitespace
  text = re.sub(r"\s+", " ", text).strip()

  return text

def wordList_preprocessing(doc_dict):
  """
  Preprocesses a dictionary of documents by removing stop words, stemming words, and creating a word list.

  Parameters:
    doc_dict (dict): A dictionary where keys are document IDs and values are the text of the documents.

  Returns:
    tuple: A tuple containing the preprocessed document dictionary and a list of stemmed words.
  """
  
  stop = StopWordRemoverFactory().get_stop_words()
  sastrawi_stemmer = StemmerFactory().create_stemmer()
  local_doc_dict = deepcopy(doc_dict)

  wordList = []
  for id, doc in doc_dict.items():
    words_in_doc = []
    cleaned_text = preprocessing(doc)
    for word in word_tokenize(cleaned_text.strip()):
      if not word in stop:
        stem_lemm_word = sastrawi_stemmer.stem(word)
        words_in_doc.append(stem_lemm_word)
        wordList.append(stem_lemm_word)

    local_doc_dict[id] = " ".join(words_in_doc)
  return local_doc_dict, wordList

def termFrequencyInDoc(vocab, doc_dict):
  """
  Calculate the term frequency of each word in a document collection.

  Parameters:
    - vocab (list): A list of unique words in the vocabulary.
    - doc_dict (dict): A dictionary where keys are document IDs and values are the text content of the documents.

  Returns:
    - tf_docs (dict): A dictionary where keys are document IDs and values are dictionaries of word frequencies for each word in the vocabulary.
  """
  tf_docs = {}
  for doc_id in doc_dict.keys():
    tf_docs[doc_id] = {}

  for word in vocab:
    for doc_id, doc in doc_dict.items():
      word_counts = Counter(doc.split())
      tf_docs[doc_id][word] = word_counts.get(word) if word_counts.get(word) else 0
  return tf_docs

def wordDocFre(vocab, doc_dict):
  """
  Calculate the frequency of each word in the given vocabulary within the document dictionary.

  Parameters:
    vocab (list): List of words to calculate frequency for.
    doc_dict (dict): Dictionary containing documents to analyze.

  Returns:
    dict: A dictionary where keys are words from vocab and values are their frequencies within the documents.
  """
  df = {}
  for word in vocab:
    frq = 0
    for doc in doc_dict.values():
      if word in regexp_tokenize(doc, '\s+', gaps=True):
        frq = frq + 1
    df[word] = frq
  return df

def inverseDocFre(vocab, doc_fre, length):
  """
  Calculate the inverse document frequency for each word in the vocabulary.

  Parameters:
      vocab (list): A list of unique words in the document.
      doc_fre (dict): A dictionary containing the document frequency of each word.
      length (int): The total number of documents.

  Returns:
      dict: A dictionary containing the inverse document frequency for each word in the vocabulary.
  """
  idf= {}
  for word in vocab:
    # idf[word] = np.log((length+1) / doc_fre[word] + 1)
    idf[word] = np.log((length + 1) / (doc_fre[word] + 1)) + 1 # smooth idf
  return idf
    
def tfidf(vocab, tf, idf_scr, doc_dict):
  """
  Calculate TF IDF scores for each word in the vocabulary for all documents in the document dictionary.
  
  Parameters:
  vocab (list): List of unique words in the vocabulary.
  tf (dict): Dictionary containing term frequency values for each document.
  idf_scr (dict): Dictionary containing inverse document frequency values for each word.
  doc_dict (dict): Dictionary containing documents indexed by their IDs.
  
  Returns:
  dict: A dictionary containing TF IDF scores for each word in the vocabulary for all documents.
  """
  tf_idf_scr = {} # TF IDF Score
  for doc_id in doc_dict.keys():
    tf_idf_scr[doc_id] = {}
  for word in vocab:
    for doc_id, doc in doc_dict.items():
      tf_idf_scr[doc_id][word] = tf[doc_id][word] * idf_scr[word]
  return tf_idf_scr

def dot_product(query_tfidf, doc_tfidf):
  """
  Calculate the dot product between the query tfidf and document tfidf.

  Parameters:
    query_tfidf (dict): A dictionary containing the tfidf values for each term in the query.
    doc_tfidf (dict): A dictionary containing the tfidf values for each term in the document.

  Returns:
    total (int): The dot product value as a result of the calculation.
  """
  # doc_tfidf => nilai tfidf setiap term dalam satu dokumen
  # query_tfidf => nilai tfidf setiap term dalam query
  total = 0
  for term in query_tfidf.keys():
    if term not in doc_tfidf:
      continue
    temp = doc_tfidf[term] * query_tfidf[term]
    total = total + temp
  return total

def vector_len(vec):
  """
  Calculate the length of a vector represented as a dictionary where keys are terms and values are coefficients.
  
  :param vec: The input vector as a dictionary.
  :return: The length of the vector as a float.
  """
  total = 0
  for term in vec.keys():
    temp = vec[term]**2
    total = total + temp
  return math.sqrt(total)

def cosim(query_tfidf, doc_tfidf):
  try:
    numerator = dot_product(query_tfidf, doc_tfidf)
    # print("atas", numerator)
    denumerator =  vector_len(query_tfidf) * vector_len(doc_tfidf)
    # print("bawah", denumerator)
    cosim = numerator/denumerator
    return cosim
  except Exception as e:
    print(e)


def query_expansion(model, query, vocab, topn=5):
  """
  Generate query baru dengan menemukan kata-kata yang serupa untuk setiap kata dalam query aslinya menggunakan model word embedding yang diberikan.

  Parameter:
      model (Word2Vec): Model word embedding untuk mencari kata-kata serupa.
      query (str): Query asli yang akan diperluas.
      vocab (set): Set kata-kata dalam vocabulary yang digunakan untuk mengfilter kata-kata yang tidak ada.
      topn (int): Jumlah kata-kata serupa yang diambil untuk setiap kata (default adalah 5).

  Returns:
      str: Query yang diperluas dengan kata-kata yang serupa dimasukkan.
  """
  sastrawi_stemmer = StemmerFactory().create_stemmer()
  new_query = [word for word in query.split()]
  for word in query.split():
    try:
      similar_word = model.wv.most_similar(word, topn=topn)
    except:
      similar_word = []

    for item in similar_word:
      if sastrawi_stemmer.stem(item[0]) in vocab and sastrawi_stemmer.stem(item[0]) not in new_query:
        new_query.append(sastrawi_stemmer.stem(item[0]))

  return " ".join(new_query)


def vectorSpaceModel(query, doc_dict, idf, tfidf_scr, qe=False, topn=5):
  """
  Fungsi untuk mencari dokumen yang relevan dengan query menggunakan metode Vector Space Model.
  Query expansion dilakukan untuk setiap kata dalam query dengan topn kata yang diperluas.
  Parameters:
    - query (str): query yang akan dicari relevannya dengan dokumen di dalam corpus
    - doc_dict (dict): dictionary yang menyimpan dokumen di dalam corpus sebagai key dan isi dokumen sebagai value
    - idf (dict): dictionary yang menyimpan idf dari setiap kata dalam global vocabulary
    - tfidf_scr (dict): dictionary yang menyimpan tfidf dari setiap kata dalam setiap dokumen di dalam corpus
    - qe (bool, optional): True jika query expansion diperbolehkan, False jika tidak. Defaults to False.
    - topn (int, optional): jumlah kata yang diperluas untuk tiap kata dalam query. Defaults to 5.
  Return:
    - sorted_value (dict): dictionary yang menyimpan relevansi setiap dokumen dengan query sebagai key dan relevansi sebagai value.
                           Semua dokumen dengan relevansi terurut dari tinggi ke rendah.
  """
  
  query_vocab = []
  query_tfidf = {}
  # case folding
  query = preprocessing(query)

  # stemming
  sastrawi_stemmer = StemmerFactory().create_stemmer()

  if(qe):
    w2v_model_200 = KeyedVectors.load("/content/idwiki_new_lower_word2vec_200.model", mmap='r')
    expanded_query = query_expansion(w2v_model_200, query, list(idf.keys()), topn=topn)
    expanded_query = sastrawi_stemmer.stem(expanded_query)
    for word in expanded_query.split():
      # kata belum masuk di query_vocab
      # tapi kata juga ada di global vocab
      if word not in query_vocab and word in idf:
        query_vocab.append(word)
        query_tfidf[word] = expanded_query.split().count(word) * idf[word]
  else:
    query = sastrawi_stemmer.stem(query)
    for word in query.split():
      # kata belum masuk di query_vocab
      # tapi kata juga ada di global vocab
      if word not in query_vocab and word in idf:
        query_vocab.append(word)
        query_tfidf[word] = query.split().count(word) * idf[word]

  # Kalau kosong atau tidak ada kata sama sekali
  if query_tfidf == {}:
    print("Tidak ditemukan dokumen dengan query :", query)
    return {}

  relevance_scores = {}
  for doc_id in doc_dict.keys():
    relevance_scores[doc_id] = cosim(query_tfidf, tfidf_scr[doc_id])

  sorted_value = OrderedDict(sorted(relevance_scores.items(), key=lambda x: x[1], reverse = True))
  print("Query : ", query)
  if(qe):
    print("Query expansion : ", expanded_query)
  top_10 = {k: sorted_value[k] for k in list(sorted_value)[:10]}
  return sorted_value

def vectorSpaceModelSklearn(query, doc_dict, idf, tfidf_scr, qe=False, topn=5):
  pass