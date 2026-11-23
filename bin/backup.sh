#!/bin/sh
# Dump the database to a compressed, restorable file.
#   DATABASE_URL=postgres://... bin/backup.sh [output-dir]
# Restore with:
#   pg_restore --clean --if-exists --no-owner -d "$DATABASE_URL" <file>.dump
set -eu
: "${DATABASE_URL:?DATABASE_URL must be set}"
OUT_DIR="${1:-backups}"
mkdir -p "$OUT_DIR"
FILE="$OUT_DIR/erp-$(date -u +%Y%m%dT%H%M%SZ).dump"
pg_dump --format=custom --no-owner --no-privileges --dbname="$DATABASE_URL" --file="$FILE"
echo "Backup written to $FILE"
