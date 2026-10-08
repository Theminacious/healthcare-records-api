# Healthcare Records API

A Django REST Framework backend for secure healthcare records management.

## Tech stack

- Django and Django REST Framework
- PostgreSQL with Django ORM
- JWT authentication with SimpleJWT
- Docker Compose for local PostgreSQL
- `python-dotenv` for environment configuration

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
docker compose up -d db
python manage.py migrate
python manage.py runserver
```

`.env` is loaded automatically and is excluded from git. Set `USE_SQLITE=true` only when running local tests without PostgreSQL.

## Authentication

### Register

`POST /api/auth/register/`

```json
{
	"name": "Ava Carter",
	"email": "ava@example.com",
	"password": "strong-pass-123"
}
```

### Login

`POST /api/auth/login/`

```json
{
	"email": "ava@example.com",
	"password": "strong-pass-123"
}
```

The response contains `access` and `refresh` JWT tokens. Send the access token with `Authorization: Bearer <token>`.

## API endpoints

### Patients

- `POST /api/patients/`
- `GET /api/patients/`
- `GET|PUT|DELETE /api/patients/<id>/`

Patients are private to the authenticated user who created them.

### Doctors

- `POST /api/doctors/`
- `GET /api/doctors/`
- `GET|PUT|DELETE /api/doctors/<id>/`

### Patient-doctor mappings

- `POST /api/mappings/` with `patient` and `doctor` IDs
- `GET /api/mappings/`
- `GET /api/mappings/<patient_id>/`
- `DELETE /api/mappings/<id>/`

Mappings are unique and can only be created for the authenticated user's patients.

## Testing

Run the complete test suite with SQLite:

```bash
DJANGO_SECRET_KEY=test-key-at-least-32-characters-long USE_SQLITE=true python manage.py test
```

The tests cover authentication, permissions, patient and doctor CRUD, mapping creation and deletion, duplicate prevention, and cross-user isolation.