set -o errexit

pip install -r requeriments.txt

python manage.py collectstatic --no-input
python manage.py migrate

python manage.py createsuperuser --username jorgepabloluis --email jorgepablolui@email.com --noinput