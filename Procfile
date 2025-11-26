web: python manage.py migrate --noinput && python manage.py import_rooms real-estate.json && python manage.py import_news_json news_data.json && python manage.py collectstatic --noinput && gunicorn config.wsgi:application --bind 0.0.0.0:$PORT --workers 3 --timeout 120

