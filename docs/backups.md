# Copias de seguridad

Toda la información del sistema vive en PostgreSQL. Todavía no hay archivos
subidos por usuarios; cuando los haya, este documento se actualiza.

## 1. Backups automáticos del proveedor (primera línea)

Usá una base PostgreSQL **administrada** con backups automáticos activados:

- **Railway:** en el servicio de Postgres → *Backups*, activar backups programados.
- **Render:** las bases pagas tienen backups diarios y restauración a un momento
  dado (*point-in-time recovery*), según el plan.
- **VPS propio:** programar `bin/backup.sh` con cron (ver punto 2) y copiar los
  archivos **fuera** del servidor (por ejemplo, a un bucket S3 o Backblaze B2).

## 2. Backup manual o programado con `bin/backup.sh`

```bash
DATABASE_URL=postgres://usuario:clave@host:5432/base bin/backup.sh ./backups
```

Genera `backups/erp-AAAAMMDDTHHMMSSZ.dump` (formato *custom* de `pg_dump`, comprimido).

Ejemplo de cron diario a las 3:15 en un VPS:

```
15 3 * * * cd /srv/erp && DATABASE_URL=... bin/backup.sh /srv/backups >> /var/log/erp-backup.log 2>&1
```

Retención sugerida: 7 diarios, 4 semanales y 6 mensuales.

## 3. Restaurar

```bash
# A una base nueva y vacía (lo más seguro: verificás antes de apuntar la app):
createdb erp_restore
pg_restore --no-owner --dbname=postgres://.../erp_restore backups/erp-XXXX.dump

# Sobre la base existente (borra y recrea los objetos):
pg_restore --clean --if-exists --no-owner --dbname="$DATABASE_URL" backups/erp-XXXX.dump
```

## 4. Probar la restauración

Un backup que nunca se restauró no está probado. Una vez por mes:

1. Restaurá el último backup en una base temporal.
2. Verificá que la app arranque contra esa base (`/healthz/`) y que los conteos
   de negocios y ventas sean razonables.
3. Borrá la base temporal.
