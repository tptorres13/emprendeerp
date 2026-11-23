# Arquitectura

## Multi-empresa (aislamiento entre negocios)

- Hay una sola base de datos y un solo esquema. Cada tabla con datos de un negocio
  tiene la columna `business_id`.
- Todos esos modelos heredan de `apps.core.models.TenantModel`:
  - `Model.objects` **siempre** filtra por el negocio activo. Si no hay negocio
    activo, lanza `TenantScopeError` (falla cerrado, nunca devuelve datos de todos).
  - `Model.unscoped` ve todos los negocios. Solo se usa para trabajo de sistema:
    admin de soporte, comandos y tareas que recorren negocios.
  - `save()` completa `business`, `created_by` y `updated_by` desde el contexto,
    y se niega a guardar una fila de otro negocio.
- `CurrentBusinessMiddleware` resuelve el negocio del usuario (a partir de
  `Membership` y la sesión) y lo activa durante toda la request con
  `apps.core.tenancy.use_business`. Un usuario logueado sin negocio va al onboarding.
- Fuera de una request (tests, comandos, tareas) hay que envolver el código en
  `with use_business(business, user): ...`.
- Tests:
  - `apps/core/tests/test_isolation.py` recorre **todos** los `TenantModel` y
    verifica que un negocio no vea las filas de otro. Si se agrega un modelo sin
    registrar su factory, el test falla.
  - Además hay tests a nivel página.

## Usuarios y roles

- `accounts.User` usa el email como login.
- `businesses.Membership` (user, business, role) define el acceso. Los roles
  `owner`, `seller` y `viewer` ya existen. Por ahora el onboarding solo crea
  dueños, y `role_required(...)` / `owner_required` protegen las vistas.

## Capas

- `models.py`: datos y restricciones.
- `services.py`: lógica de negocio, en transacciones (`create_business`, ...).
  Las vistas no tienen lógica de negocio.
- `views.py` / `forms.py` / `templates/`: interfaz. HTMX para interacciones
  parciales, Tailwind para estilos.

## Interfaz

- Pensada primero para el celular: barra inferior en celular, barra lateral desde `md`.
- Todos los formularios (los propios y los de allauth) se dibujan con
  `templates/forms/*.html` (`FORM_RENDERER`), así se ven igual en todos lados.
- Los textos visibles van en español rioplatense. Los textos que vienen de
  librerías se sobreescriben en `locale/es_AR/LC_MESSAGES/django.po`. Después de
  editarlo, correr `uv run python manage.py compilemessages --ignore=.venv`
  (el `.mo` compilado se versiona).
- La navegación se define en `apps/core/navigation.py`. Cada módulo suma su
  entrada cuando sale.

## Seguridad

- Contraseñas con Argon2 y validadores de Django (largo mínimo de 8, contraseñas
  comunes, solo números, parecido a los datos personales).
- Límite de intentos de login por IP y por cuenta (allauth), usando la caché en
  base de datos, compartida entre workers.
- CSRF en todos los formularios. HTMX manda el token en el header `X-CSRFToken`.
- `LoginRequiredMiddleware`: todas las vistas requieren login, salvo las
  marcadas con `@login_not_required`.
- Producción: HTTPS obligatorio, cookies `Secure`, HSTS, `X-Frame-Options: DENY`,
  `nosniff`, admin en una URL configurable (`ADMIN_URL`). La CI corre
  `check --deploy`.
- El admin muestra datos de negocios solo en lectura (`TenantReadOnlyAdmin`).

## Reglas para lo que viene (Fase 1 en adelante)

- Dinero: `DecimalField`, nunca `float`.
- El stock y la caja son registros de solo agregar: no se editan ni se borran, y
  un error se corrige con un contra-movimiento.
- Las integraciones externas van detrás de una interfaz propia (adaptador), con
  una implementación falsa para desarrollo y tests.
