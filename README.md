# Social Media API 👩🏻‍💻

Social Media API a RESTful API for a social media platform.
The API allows users to create profiles, follow other users,
create and retrieve posts, manage likes and comments, and perform basic social media actions.

## Technologies

- Django Rest Framework
- Postgres
- Docker

## Installing using GitHub

Install PostgresSQL and create database

```
git clone https://github.com/MatsalakO/social-meda-api
cd social_media_api
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
set DJANGO_SECRET_KEY=<yoursecretkey>
set POSTGRES_HOST=<your db host name>
set POSTGRES_DB=<your db name>
set POSTGRES_USER=<your db username>
set POSTGRES_PASSWORD=<your db password>
python manage.py migrate
python manage.py runserver
```

# Run with Docker

Install and create account in Docker first

```
docker-compose build
docker-compose up
```

## Features

- JWT authentication (with logout function)
- Admin panel via /admin/
- Documentation via /api/doc/swagger/
- Extended profile system for users
- Likes, comments and following system
- CRUD operations for posts, comments
- Upload media to post
- Retrieving posts by present hashtag
