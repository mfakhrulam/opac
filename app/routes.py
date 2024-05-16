from app import app, db, api
from app.api_utils import read_index
from app.models import Doc, User
from flask import flash, redirect, render_template, request, url_for
from helper import preprocessing, query_expansion
from sklearn.metrics.pairwise import cosine_similarity
from PaginatedObj import PaginateObj
from flask_login import current_user, login_user, logout_user, login_required

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
  nqe = request.args.get("nqe") or 0
  query = request.args.get("query").strip()
  curr_page = request.args.get("page") or 1
  if not query:
    return redirect(url_for('index')) 
    
  tf_idf_vectorizer, tf_idf_sparse = read_index()
  docs = Doc.query.all() # return dalam bentuk list
  
  # logic preprocessing dan QE
  query = preprocessing(query)
  sastrawi_stemmer = StemmerFactory().create_stemmer()
  # stop = StopWordRemoverFactory().get_stop_words()
  # stopword (kayaknya perlu dihapus)
  # query = " ".join([word for word in query.split() if word not in stop])
  # cek lebih baik stem dulu atau stem belakangan (di sini)
  query = sastrawi_stemmer.stem(query)
  print('query awal: ', query)
  
  if request.args.get('qe') == 'w2v':
    vocab = tf_idf_vectorizer.get_feature_names_out()
    # TODO 
    # ganti query_expansion logic to return two results
    #  1. original query
    #  2. query expansion
    query = query_expansion(w2v_model, query, vocab, topn=int(nqe))
    query = sastrawi_stemmer.stem(query)  
  
  # transform ke vector
  # TODO
  # kalau semisal ingin menghitung query expansion re-weighting 
  # berarti nanti di sini nilainya tidak serta merta ditransform
  # menggunakan tf_idf_vectorizer,
  # mesti dihitung manual, tetapi tetap memanfaatkan tf_idf_sparse
  query_vector = tf_idf_vectorizer.transform([query])
  # contoh output
  # query awal:  cari tempat
  # (0, 4441)     6.845153427837061
  # (0, 2519)     4.711644664886949
  # (0, 741)      4.7657118861572245
  # query akhir: cari tempat lokasi
  # Nah di sini harus diolah nilai tf-idfnya
  
  cosine_similarities = cosine_similarity(query_vector, tf_idf_sparse)
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
@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
  if current_user.is_authenticated:
      return redirect(url_for('index'))
  if request.method == "POST":
    username = request.form.get('username')
    password = request.form.get('password')
    remember = True if request.form.get('remember') else False

    user = User.query.filter_by(username=username).first()

    if not user or not user.check_password(password):
      flash('Mohon cek kembali username dan password Anda.')
      return redirect(url_for('admin_login')) # if the user doesn't exist or password is wrong, reload the page

    # if the above check passes, then we know the user has the right credentials
    login_user(user, remember=remember)
    return redirect(url_for('index'))
  return render_template("admin/login.html")

@app.route("/admin/logout", methods=["GET", "POST"])
def admin_logout():
  logout_user()
  return redirect(url_for('index'))

@app.route("/admin/docs")
@login_required
def admin_docs():
  curr_page = request.args.get("page") or 1
  page = Doc.get_paginated_docs(int(curr_page),  per_page=10)
  return render_template("admin/docs/home_docs.html", page=page)
