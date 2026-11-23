# Emprende (nombre de trabajo)

ERP en la nube para emprendedores argentinos: stock, ventas, compras, caja y envíos,
simple y pensado primero para el celular.

> **Estado:** Fase 0 (base del proyecto) terminada. Ver [Fases](#fases).

## Stack

| Capa | Tecnología |
|---|---|
| Backend | Python 3.13 · Django 5.2 LTS |
| Base de datos | PostgreSQL 17 |
| Frontend | Plantillas Django + HTMX + Tailwind CSS v4 (binario standalone, sin Node) |
| Auth | django-allauth (login con email, recuperación de contraseña, límite de intentos) |
| Tests / calidad | pytest, pytest-django, factory_boy, coverage, ruff, pre-commit |
| Dependencias | [uv](https://docs.astral.sh/uv/) (`pyproject.toml` + `uv.lock`) |
| Producción | Docker (gunicorn + whitenoise), configurable por variables de entorno |

## Cómo levantarlo

### Opción A: Docker Compose (recomendada)

```bash
docker compose up --build
```

- App: http://localhost:8000
- Emails que manda la app (por ejemplo, recuperar contraseña): http://localhost:8025 (Mailpit)

### Opción B: Sin Docker

Necesitás Python 3.13, [uv](https://docs.astral.sh/uv/) y un PostgreSQL corriendo.

```bash
cp .env.example .env              # ajustá DATABASE_URL si hace falta
uv sync
uv run python manage.py migrate
uv run python manage.py createcachetable
uv run python manage.py tailwind runserver   # Django + recompilación de CSS
```

Para entrar al panel de administración (soporte), creá un superusuario:

```bash
uv run python manage.py createsuperuser
```

## Tests y calidad

```bash
uv run pytest --cov          # tests + cobertura (mínimo 90%)
uv run ruff check .          # linter
uv run ruff format .         # formateador
uv run pre-commit install    # corre ruff antes de cada commit
```

Los tests necesitan PostgreSQL (usan `DATABASE_URL`, por defecto
`postgres://postgres:postgres@localhost:5432/erp`).

La CI (GitHub Actions) corre linter, formato, migraciones pendientes, tests con
cobertura, `check --deploy` con la configuración de producción y el build de la
imagen Docker.

## Configuración por entorno

| Archivo | Uso |
|---|---|
| `config/settings/base.py` | Común a todos los entornos |
| `config/settings/dev.py` | Desarrollo local (por defecto en `manage.py`) |
| `config/settings/test.py` | Tests (lo usa pytest) |
| `config/settings/prod.py` | Producción (lo usa la imagen Docker y `wsgi.py`) |

Variables de entorno: ver [`.env.example`](.env.example). **Ningún secreto va en el código.**

## Despliegue

La imagen de producción (`docker build --target prod .`) sirve para Railway,
Render o un VPS:

1. Crear una base PostgreSQL administrada y setear `DATABASE_URL`.
2. Setear `DJANGO_SECRET_KEY` (valor largo y aleatorio), `DJANGO_ALLOWED_HOSTS`,
   `DJANGO_CSRF_TRUSTED_ORIGINS`, `EMAIL_URL`, `DEFAULT_FROM_EMAIL` y `ADMIN_URL`.
3. El contenedor ejecuta `bin/start.sh`: aplica migraciones, crea la tabla de
   caché y levanta gunicorn en `$PORT`.
4. Health check: `GET /healthz/`.

Backups: ver [docs/backups.md](docs/backups.md).

Guía de herramientas explicada sin tecnicismos: [docs/herramientas.md](docs/herramientas.md).

## Estructura

```
config/            settings por entorno, urls, wsgi
apps/
  core/            base multi-empresa (TenantModel), navegación, vistas comunes
  accounts/        usuario (login con email), formularios y adapter de allauth
  businesses/      negocio, membresías/roles, onboarding, middleware del negocio activo
  catalog/         categorías (productos en Fase 1)
templates/         plantillas (layouts, formularios, pantallas de acceso en rioplatense)
assets/            fuente de Tailwind (compila a static/css/app.css)
locale/es_AR/      traducciones rioplatenses de textos de Django y allauth
docs/              arquitectura, backups y registro de decisiones
```

Más detalle en [docs/architecture.md](docs/architecture.md).

## Fases

- [x] **Fase 0. Base:** repositorio, Docker, configuración por entorno y CI; registro, login, recuperación de contraseña y límite de intentos; negocio, membresía y aislamiento entre negocios; onboarding de 3 pasos con categorías por rubro; layout pensado primero para el celular.
- [ ] **Fase 1. Lo esencial:** en entregas 1a a 1f (circuito mínimo, productos, clientes y ventas, compras, caja, tablero).
- [ ] **Fase 2. Para crecer**
- [ ] **Fase 3. Para equipos**
