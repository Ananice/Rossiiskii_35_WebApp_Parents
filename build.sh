set -e

pip install -r requirements.txt
python manage.py collectstatic --no-input
python manage.py migrate

if [ "${AUTO_CREATE_DEMO_USERS:-0}" = "1" ]; then
  python manage.py create_demo_users || true
fi
