# Gunakan image dasar yang memiliki Python
FROM python:3.9.7

# Tentukan direktori kerja di dalam container
WORKDIR /app

# Install dependencies untuk mysqlclient
RUN apt-get update && apt-get install -y \
    build-essential \
    libssl-dev \
    libffi-dev \
    libmariadb-dev

# Salin requirements.txt dan install dependencies
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Install dependencies untuk Flowbite 
RUN apt-get update && apt-get install -y nodejs npm
COPY package.json package-lock.json ./
RUN npm install

# Salin seluruh kode aplikasi ke dalam container
COPY . .

# Install unzip tool untuk mengekstrak file
RUN apt-get update && apt-get install -y unzip

# Salin script dan berikan izin eksekusi
COPY download_model.sh .
RUN chmod +x download_model.sh

# Jalankan script untuk mendownload dan meng-unzip model dari Google Drive
RUN ./download_model.sh

# Download NLTK data
RUN python -m nltk.downloader punkt

# Jalankan migrasi database
RUN flask db init
RUN flask db migrate -m "Initial migration"
RUN flask db upgrade

RUN python init_db.py

# Tentukan command untuk menjalankan aplikasi menggunakan Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]
