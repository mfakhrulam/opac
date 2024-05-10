from app import app, db, api
from app.api_utils import read_index
from app.models import Doc
from flask import redirect, render_template, request, url_for
from helper import preprocessing, query_expansion
from sklearn.metrics.pairwise import cosine_similarity
from PaginatedObj import PaginateObj

from Sastrawi.Stemmer.StemmerFactory import StemmerFactory
from Sastrawi.StopWordRemover.StopWordRemoverFactory import StopWordRemoverFactory

from gensim.models import KeyedVectors
from config import Config


app.register_blueprint(api.api)

w2v_model = KeyedVectors.load(Config.W2V_MODEL, mmap='r')

@app.route("/")
@app.route("/index")
@app.route("/docs")
def index():
  # columns = ['id', 'title', 'year', 'author', 'classification', 'subject', 'publisher', 'abstract', 'location']
  # df = pd.read_sql(db.session.query(Doc).statement, db.session.connection())
  # df = df[columns]
  
  curr_page = request.args.get("page") or 1
  page = Doc.get_paginated_docs(int(curr_page), per_page=10)
  total_docs = db.session.query(Doc).count()
  return render_template("index.html", page=page, total_docs=total_docs)

@app.route("/search")
def search():
  # TODO
  # Implementasikan jumlah kata untuk QE
  
  nqe = request.args.get("nqe") or 1
  query = request.args.get("query").strip()
  curr_page = request.args.get("page") or 1
  if not query:
    return redirect(url_for('index')) 
    
  tf_idf_vectorizer, tf_idf_sparse = read_index()
  docs = Doc.query.all() # return dalam bentuk list
  
  # logic preprocessing dan QE
  query = preprocessing(query)
  sastrawi_stemmer = StemmerFactory().create_stemmer()
  stop = StopWordRemoverFactory().get_stop_words()
  # stopword (kayaknya perlu dihapus)
  # query = " ".join([word for word in query.split() if word not in stop])
  # cek lebih baik stem dulu atau stem belakangan (di sini)
  query = sastrawi_stemmer.stem(query)
  print('query awal: ', query)
  
  if request.args.get('qe') == 'w2v':
    vocab = tf_idf_vectorizer.get_feature_names_out()
    query = query_expansion(w2v_model, query, vocab, topn=int(nqe))
    query = sastrawi_stemmer.stem(query)  
  
  # transform ke vector
  query_vector = tf_idf_vectorizer.transform([query])
  cosine_similarities = cosine_similarity(query_vector, tf_idf_sparse)
  # results = [(docs_raw['id'][i], cosine_similarities[0][i]) for i in range(len(docs_raw))]  # awal
  docs_similarities = [(docs[i].id, cosine_similarities[0][i]) for i in range(len(docs))]
  docs_similarities.sort(key=lambda x: x[1], reverse=True)
  docs_similarities_score = [doc_similarity[1] for doc_similarity in docs_similarities if doc_similarity[1] > 0]
  paginated_docs_similarities_score = PaginateObj(docs_similarities_score, int(curr_page), 10) #returns the first page of 10 elements

  doc_ids = [doc_similarity[0] for doc_similarity in docs_similarities if doc_similarity[1] > 0]
  # query_results = Doc.query.filter(Doc.id.in_(doc_ids)).order_by(func.idx(doc_ids, Doc.id)) # error
  total_docs = len(doc_ids)
  
  order_expressions = [(Doc.id==i).desc() for i in doc_ids]
  query_results = Doc.query.filter(Doc.id.in_(doc_ids)).order_by(*order_expressions)
  paginated_results = query_results.paginate(page=int(curr_page), per_page=10, error_out=False)
  zip_results = zip(paginated_results, paginated_docs_similarities_score.items)

  print('query akhir:', query)
  return render_template('index.html', page=paginated_results, total_docs=total_docs, zip_results=zip_results)


@app.route("/docs/<int:id>")
def docs(id):
  return render_template("docs.html", id=id)

@app.route("/qe", methods=["GET", "POST"])
def qe():
  if not request.args.get('query'):
    return render_template("qe.html", result='')
  query = request.args.get("query")
  query = preprocessing(query)
  nqe = request.args.get("nqe") or 1
  tf_idf_vectorizer, _= read_index()
  vocab = tf_idf_vectorizer.get_feature_names_out()
  query = query_expansion(w2v_model, query, vocab, topn=int(nqe))
  return render_template("qe.html", result=query)

# ======== ADMIN ========
@app.route("/admin/login")
def admin_login():
  return render_template("admin/login.html")

@app.route("/admin/docs")
def admin_docs():
  curr_page = request.args.get("page") or 1
  page = Doc.get_paginated_docs(int(curr_page),  per_page=10)
  return render_template("admin/docs/home_docs.html", page=page)
