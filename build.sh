#!/usr/bin/env bash

pip install -r requirements.txt

python manage.py collectstatic --noinput
python manage.py flush --noinput
python manage.py migrate

echo "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.filter(username='admin').exists() or User.objects.create_superuser('admin','admin@gmail.com','admin123')" | python manage.py shell
