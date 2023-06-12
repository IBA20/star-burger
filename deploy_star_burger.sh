#!/bin/bash
set  -e
docker compose down --rmi local
git pull
docker compose up -d
docker compose exec backend ./manage.py migrate --noinput
echo "Deploy successful!!!"

