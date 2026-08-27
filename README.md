# News Application — Django Capstone Project

A Django news platform where **journalists** write articles, **editors**
review and approve them, and **readers** browse approved articles and
newsletters — via both a web front end and a token-authenticated REST API
(Django REST Framework). Approving an article emails subscribed readers
and notifies the internal API automatically via a Django signal.

## Project layout

```
newsproject/    Project settings, root URL config, WSGI/ASGI entry points
newsapp/        Models, views, forms, admin, signals, and the REST API
templates/      HTML templates for the web front end
docs/           Sphinx documentation source and generated HTML (docs/_build/html)
Dockerfile      Container image definition
docker-compose.yml  App + MariaDB, for one-command local/Docker Playground runs
entrypoint.sh   Container startup script (migrate, setup_permissions, gunicorn)
.env.example    Template for environment variables - copy to .env and edit
requirements.txt
```

> **Note on this repository:** the project is committed as plain files and
> folders (not a `.zip`), so GitHub's normal features - browsing files,
> viewing diffs, `git clone`, etc. - work as expected. If you ever
> downloaded this project as a `.zip`, extract it and push the extracted
> folder itself; don't commit a `.zip` archive to a GitHub repo.

## Prerequisites

- Python 3.12+
- Git
- MariaDB/MySQL server (or use the SQLite fallback described below)
- Docker Desktop (or the Docker daemon) and Docker Compose, if you want
  to run the app in containers instead

## Getting the project

Both options below start the same way. Open a terminal and run:

```bash
git clone <repo link>
cd newsapp-capstone
```

Replace `<repo link>` with this repository's clone URL (copy it from the
green **Code** button on GitHub), and replace `newsapp-capstone` with
whatever folder name `git clone` actually created on your machine - it's
the repository's name. Everything below (creating a venv, installing
`requirements.txt`, building the Docker image, copying `.env.example`)
is run **from inside that project folder**, since that's where
`requirements.txt`, `manage.py`, the `Dockerfile`, etc. all live.

## Option 1: Run locally with venv

1. **Create and activate a virtual environment** (inside the project
   folder, so a new `venv/` folder appears next to `manage.py`):
   ```bash
   python -m venv venv
   source venv/bin/activate      # Windows: venv\Scripts\activate
   ```

2. **Install dependencies** (still inside the project folder, so
   `requirements.txt` is found):
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up your environment variables.** Copy the provided template and
   edit it with your own values:
   ```bash
   cp .env.example .env          # Windows: copy .env.example .env
   ```
   Open `.env` in a text editor and fill in your database credentials
   (and, optionally, email settings - see below). `.env` lives in the
   project's root folder, next to `manage.py`; it's read automatically
   and is already excluded via `.gitignore`, so it's never committed.

   By default `.env.example` configures a MariaDB/MySQL connection. If
   you don't have MariaDB/MySQL installed, open `.env` and set
   `USE_SQLITE=1` instead - this skips the database steps below entirely
   and uses a local SQLite file.

4. **Create the database** (skip this step if you set `USE_SQLITE=1`):
   ```bash
   mysql -u root -p -e "CREATE DATABASE newsdb CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
   ```
   Use the same database name you put in `.env` (`newsdb` by default).

5. **Apply migrations and set up roles**
   ```bash
   python manage.py migrate
   python manage.py setup_permissions
   python manage.py createsuperuser
   ```

6. **Run the development server**
   ```bash
   python manage.py runserver
   ```
   Visit `http://localhost:8000`.

7. **Run the test suite**
   ```bash
   USE_SQLITE=1 python manage.py test
   ```

### Email and API notification settings (optional)

Approving an article triggers an email to subscribed readers and a POST
to the app's own `/api/approved/` endpoint. By default, email is printed
to the console (no real email is sent) - you don't need to configure
anything for this to work in development. To send real email instead,
set `EMAIL_HOST_USER` and `EMAIL_HOST_PASSWORD` in your `.env` file (use
a Gmail **App Password**, not your normal login password), then switch
`EMAIL_BACKEND` in `newsproject/settings.py` to the SMTP backend (see the
comment above it in that file). Never commit real credentials - keeping
them in `.env` (untracked) is what keeps them out of GitHub.

## Option 2: Run with Docker

This option is self-contained: you do **not** need a venv, and you do
**not** need to install `requirements.txt` yourself - both the app's
dependencies and the app itself are installed inside the Docker image
by the `Dockerfile` when you build it.

1. **Start Docker Desktop** (or make sure the Docker daemon is running)
   before doing anything else. `docker compose` and `docker build` will
   fail with a connection error if it isn't running.

2. **Get the project**, if you haven't already (see
   [Getting the project](#getting-the-project) above):
   ```bash
   git clone <repo link>
   cd newsapp-capstone
   ```
   You now have access to the `Dockerfile` and `docker-compose.yml` used
   in the steps below, since both live in this project folder.

3. **(Optional) set your environment variables.** Copy the template:
   ```bash
   cp .env.example .env          # Windows: copy .env.example .env
   ```
   and edit `.env` with your own database/email values. Docker Compose
   automatically loads a `.env` file from this same folder - no extra
   flags needed. If you skip this step, sensible defaults baked into
   `docker-compose.yml` are used instead.

4. **Build and start everything**
   ```bash
   docker compose up --build
   ```
   This builds the app image from the `Dockerfile`, starts a `db`
   container (MariaDB) and a `web` container (the Django app served by
   gunicorn), applies migrations, and runs `setup_permissions`
   automatically via `entrypoint.sh`.

5. **Visit the app** at `http://localhost:8000`.

6. **Create an admin user** (in a second terminal, while the containers
   are running):
   ```bash
   docker compose exec web python manage.py createsuperuser
   ```

7. **Stop everything**
   ```bash
   docker compose down          # add -v to also delete the database volume
   ```

### Building/running just the image (no Compose)

If you only have `docker build`/`docker run` available (e.g. the Docker
Playground), you can run the app against SQLite instead of MariaDB so no
separate database container is needed. Docker Desktop still needs to be
running, and this still assumes you're inside the project folder from
step 2 above, since that's where the `Dockerfile` is:
```bash
docker build -t newsapp .
docker run -p 8000:8000 -e USE_SQLITE=1 newsapp
```

## Documentation

Full auto-generated API documentation (built with Sphinx from the
project's docstrings) is available at `docs/_build/html/index.html` -
open that file directly in a browser, or rebuild it yourself:
```bash
pip install sphinx
USE_SQLITE=1 sphinx-build -b html docs docs/_build/html
```

## Notes on the codebase

This project underwent a round of bug-fixing before this submission,
including: removing a circular/forward-referencing foreign key setup,
resolving a `related_name` clash between subscription fields, adding a
missing `timezone` import used in `Article.save()`, converting two
notification helpers from (incorrect) instance methods into standalone
functions, fixing missing imports in the API views, and switching the
permissions management command to `get_or_create` so it can be re-run
safely.

## Git branches

- `master` — main branch, contains everything merged together
- `docs` — docstrings added file-by-file, plus the generated Sphinx docs
- `container` — Docker/Compose setup for containerised deployment
