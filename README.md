# Healthcare Backend

Django REST Framework backend for authentication, patients, doctors, and patient-doctor assignments.

## Run locally

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
docker compose up -d db
python manage.py makemigrations core
python manage.py migrate
python manage.py runserver
```

Set `USE_SQLITE=true` to run checks and tests without PostgreSQL. Normal development and production use PostgreSQL settings from the environment.

## Endpoints

- `POST /api/auth/register/` with `name`, `email`, and `password`
- `POST /api/auth/login/` with `email` and `password`
- `POST|GET /api/patients/`, plus `GET|PUT|DELETE /api/patients/<id>/`
- `POST|GET /api/doctors/`, plus `GET|PUT|DELETE /api/doctors/<id>/`
- `POST|GET /api/mappings/`, `GET /api/mappings/<id>/`, and `DELETE /api/mappings/<id>/`

Send the access token as `Authorization: Bearer <token>`.