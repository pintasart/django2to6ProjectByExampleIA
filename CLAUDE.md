# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

This repository contains four independent Django projects from the "Django by Example" book series. Each project lives in its own directory and is self-contained. A shared virtual environment is at `venv/`.

| Project | Focus |
|---------|-------|
| `mysite/` | Blog platform — models, admin, sitemaps, tags, feeds |
| `myshop/` | E-commerce — cart, orders, payment, Celery, i18n |
| `bookmarks/` | Social bookmarking — OAuth, image thumbnails, activity streams |
| `educa/` | Education platform — REST API, generic FK content, subdomain middleware |

## Environment

```bash
source venv/bin/activate        # activate shared venv (Python 3.12, Django 6.0.4)
```

## Common Commands

All commands run from inside the project directory (e.g., `cd mysite`).

```bash
python manage.py runserver
python manage.py makemigrations && python manage.py migrate
python manage.py createsuperuser

# educa uses a split settings layout
python manage.py runserver --settings=educa.settings.local
```

### Tests

```bash
pytest                          # run all tests in current project
pytest <app>/tests.py -v        # run a specific test file
```

### Linting

```bash
flake8 <project>/               # no project-level config; uses defaults
```

### Translations (myshop only)

```bash
django-admin makemessages --all
django-admin compilemessages
```

### Fixtures (educa)

```bash
python manage.py dumpdata courses --indent=2 --output=courses/fixtures/subjects.json
python manage.py loaddata subjects.json
```

## Architecture Notes

### Settings

- **mysite, myshop, bookmarks**: single `settings.py` with `DEBUG=True`, hardcoded credentials (dev only)
- **educa**: split into `educa/settings/base.py`, `local.py`, `pro.py`
- No `.env` files; credentials are inline in settings for learning purposes

### Databases

- **mysite**: PostgreSQL (`host=localhost`, user `blog`, password `1234`)
- **myshop, bookmarks, educa**: SQLite (`.sqlite3` files already present)

### External Services

| Service | Used by | Default |
|---------|---------|---------|
| Redis | bookmarks (DB 0), myshop (DB 1) | `localhost:6379` |
| RabbitMQ | myshop Celery broker | `amqp://guest:guest@localhost` |
| Braintree | myshop payment | credentials placeholder in settings |
| Facebook/Twitter/Google OAuth | bookmarks | credentials placeholder in settings |

### Key Patterns

- **mysite/blog**: Custom `PublishedManager` on `Post`; `taggit` for tagging
- **myshop**: Session-based cart (`CART_SESSION_ID = 'cart'`); `django-parler` for multilingual `Category`/`Product`; Celery tasks in `orders/tasks.py`
- **bookmarks**: `EmailAuthBackend` custom authentication backend; `sorl-thumbnail` generates thumbnails via signals on `Image` save; activity stream via `actions` app
- **educa**: `Content` model uses a `GenericForeignKey` to `Text | File | Image | Video` subclasses of abstract `ItemBase`; custom `OrderField` for sequencing; `SubdomainCourseMiddleware` maps subdomains to courses; Django REST Framework for the API
