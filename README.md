Activate the python environment
`.\.venv\Scripts\activate`

Install the requirement
`pip install -r requirements.txt`
`npm install`

Change this file name .flaskenv.tmp to  .flaskenv


Run the following command to compile and watch for changes for the Tailwind CSS file:  
`npx tailwindcss -i ./app/static/src/input.css -o ./app/static/dist/css/output.css --watch`

Migrate db
`flask db migrate`

Run flask
`flask run`

Generate admin
``` python
from app import app, db
from app.models import User
import sqlalchemy as sa
app.app_context().push()
u = User(username='admin')
u.set_password('admin123#')
db.session.add(u)
db.session.commit()
```


Add the documents you want


# Sistem Pencarian Dokumen Skripsi dengan Query Expansion

Ini adalah sistem pencarian dokumen skripsi berbasis web yang dikembangkan menggunakan Flask dan database MySQL. Sistem ini juga menggunakan framework Flowbite untuk styling dan mendownload model dari Google Drive.

## Fitur

- Pencarian dokumen skripsi dengan query expansion
- Web interface dengan Flask
- Styling dengan Flowbite
- Penyimpanan data menggunakan MySQL
- Penggunaan Docker untuk mempermudah deployment
- Mendownload dan menggunakan model dari Google Drive

## Prasyarat

- Docker dan Docker Compose harus sudah terinstal di sistem Anda.
- Koneksi internet untuk mendownload dependensi dan model dari Google Drive.

## Instalasi dan Penggunaan

### 1. Clone Repository

Clone repository ini ke komputer lokal Anda:

```bash
git clone https://github.com/username/repository.git
cd repository
```

### 2. Konfigurasi Environment
Buat file .env di root proyek Anda dan tambahkan konfigurasi berikut:

```dotenv
MYSQL_HOST=db
MYSQL_USER=root
MYSQL_PASSWORD=example
MYSQL_DB=skripsi
```

### 3. Build dan Jalankan Docker Containers

Bangun dan jalankan container menggunakan Docker Compose:

```bash
git clone https://github.com/username/repository.git
cd repository
```

Perintah ini akan melakukan hal berikut:

- Membangun image Docker untuk aplikasi Flask Anda.
- Menjalankan container untuk aplikasi Flask dan MySQL.
- Mendownload dan meng-unzip model dari Google Drive.
- Mendownload data NLTK 'punkt'.

### 4. Akses Aplikasi

Akses aplikasi di browser Anda pada http://localhost:5000.

## Script untuk Mendownload dan Meng-unzip File dari Google Drive

File download_and_unzip.sh digunakan untuk mendownload dan meng-unzip file dari Google Drive ke direktori we_model. Pastikan untuk mengganti your_google_drive_file_id dengan ID file Google Drive yang sebenarnya.

```bash
#!/bin/bash

# Ganti dengan URL file Google Drive Anda
FILE_ID="your_google_drive_file_id"
DESTINATION="/app/we_model/your_file.zip"

# Download file dari Google Drive
curl -L -o $DESTINATION "https://drive.google.com/uc?export=download&id=${FILE_ID}"

# Unzip file
unzip $DESTINATION -d /app/we_model
```

## Kontak

Jika Anda memiliki pertanyaan lebih lanjut atau butuh bantuan, silakan hubungi saya di email [berikut](aminfakhrul@gmail.com).