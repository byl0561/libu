#!/bin/sh
# Container entrypoint: generate site-wide Basic Auth from env, start nginx, then
# exec gunicorn (FastAPI). Tables are created on app startup (lifespan), no migration step.
set -e

# Site-wide HTTP Basic Auth. nginx.conf `include`s /etc/nginx/auth.conf at server
# scope; generate it (and the htpasswd) from APP_USERNAME / APP_PASSWORD here.
# Empty APP_PASSWORD => empty include => auth disabled (handy for local/dev).
# {SHA} is nginx-supported so we need no apache2-utils just to hash one password.
: > /etc/nginx/auth.conf
if [ -n "$APP_PASSWORD" ]; then
  python -c "import base64,hashlib,os;u=os.environ.get('APP_USERNAME') or 'admin';p=os.environ['APP_PASSWORD'];open('/etc/nginx/.htpasswd','w').write(u+':{SHA}'+base64.b64encode(hashlib.sha1(p.encode()).digest()).decode()+'\n')"
  printf 'auth_basic "Libu";\nauth_basic_user_file /etc/nginx/.htpasswd;\n' > /etc/nginx/auth.conf
else
  echo "entrypoint: APP_PASSWORD empty -> Basic Auth DISABLED (set it for internal use!)" >&2
fi

nginx -g 'daemon off;' &

exec gunicorn app.main:app \
  -k uvicorn.workers.UvicornWorker \
  --bind 127.0.0.1:8000 \
  --workers "${GUNICORN_WORKERS:-2}" \
  --timeout "${GUNICORN_TIMEOUT:-120}"
