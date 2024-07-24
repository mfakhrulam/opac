# Tunggu database siap
while ! nc -z db 3306; do
  echo "Waiting for MySQL..."
  sleep 1
done

# Jalankan migrasi database jika direktori migrations belum ada
if [ ! -d "migrations" ]; then
  flask db init
  flask db migrate -m "Initial migration" || true
fi
flask db upgrade || true

python init_db.py
# Jalankan aplikasi
exec "$@"