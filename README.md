# Advanceportfolio

For local development, start Django with `python manage.py runserver`; Django creates a temporary secret key when `DJANGO_SECRET_KEY` is unset. Sessions and other signed data will reset when the server restarts in that mode.

For deployments, set a persistent, private `DJANGO_SECRET_KEY` and set `DJANGO_DEBUG=0`. Django refuses to start with debug disabled if the secret key is missing. The local SQLite database is intentionally excluded from Git.
