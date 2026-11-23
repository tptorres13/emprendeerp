# 0001. Stack y modelo multi-empresa

**Estado:** aceptada (Fase 0)

## Decisiones

1. **Django 5.2 LTS.** Tiene soporte hasta abril de 2028. Se migra a la próxima
   LTS cuando salga.
2. **Una base y un esquema compartidos, con `business_id` en cada tabla**, en
   lugar de un esquema por negocio (django-tenants). Es más simple de migrar y
   de alojar en hostings económicos, y el aislamiento se garantiza con:
   - un manager que **falla cerrado** si no hay negocio activo;
   - `save()` que se niega a escribir en otro negocio;
   - un test que recorre todos los modelos del negocio.

   Si más adelante hace falta, se puede sumar Row-Level Security de PostgreSQL
   como segunda barrera.
3. **django-allauth** para la autenticación: registro, login por email,
   recuperación de contraseña y límite de intentos sin código propio, y deja
   abierta la puerta a "Entrar con Google".
4. **Caché en base de datos** en lugar de Redis: los límites de intentos se
   comparten entre workers sin sumar un servicio.
5. **Tareas en segundo plano: django-q2 con PostgreSQL como cola.** Se agrega
   recién en la Fase 2, cuando haga falta.
6. **Tailwind v4 con el binario standalone** (django-tailwind-cli): no hace falta
   Node en ninguna etapa.
7. **uv instalado desde PyPI en el Dockerfile**, para no depender del registry
   de imágenes de GitHub al construir.
