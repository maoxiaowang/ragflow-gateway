#!/bin/sh
set -e

[ -n "$LOG_DIR" ] && mkdir -p "$LOG_DIR"
[ -n "$UPLOAD_DIR" ] && mkdir -p "$UPLOAD_DIR"

exec "$@"