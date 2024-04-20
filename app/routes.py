from app import app
from flask import redirect, render_template, request, url_for
from process_docs import get_list_docs, load_vectorizer_sparse
from sklearn.metrics.pairwise import cosine_similarity

@app.route("/")
@app.route("/index")
@app.route("/docs")
def index():
	return render_template("index.html")

@app.route("/search")
def search():
  query = request.args.get("query")
  if not query:
    return redirect(url_for('index')) 
  
  docs_raw = get_list_docs(input_data='title_only')
  
  vectorizer_path = './pickle_model/tf_idf_vectorizer.pkl'
  sparse_path = './pickle_model/tf_idf_sparse.pkl'
  
  tf_idf_vectorizer, tf_idf_sparse = load_vectorizer_sparse(vectorizer_path, sparse_path)
  
  query_vector = tf_idf_vectorizer.transform([query])
  cosine_similarities = cosine_similarity(query_vector, tf_idf_sparse)
  results = [(docs_raw[i], cosine_similarities[0][i]) for i in range(len(docs_raw))]
  results.sort(key=lambda x: x[1], reverse=True)
  for doc, similarity in results[:10]:
    if similarity > 0:
      print(f"Similarity: {similarity:.6f} - {doc}\n")

  return render_template("index.html")

@app.route("/docs/<int:id>")
def docs(id):
  return render_template("docs.html", id=id)

@app.route("/admin/docs")
def admin_docs():
  return render_template("admin/docs/home_docs.html")

@app.route("/admin/login")
def admin_login():
  return render_template("admin/login.html")


