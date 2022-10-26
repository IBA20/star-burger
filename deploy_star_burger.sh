#!/bin/bash
set  -e
git pull
./venv/bin/pip install -r requirements.txt
npm install
nohup ./node_modules/.bin/parcel watch bundles-src/index.js --dist-dir bundles --public-url="./" &
./venv/bin/python manage.py collectstatic --noinput
./venv/bin/python manage.py migrate
systemctl restart star-burger
curl \
    -H "X-Rollbar-Access-Token: 5373b8187af44c3199700e59c7212f3c" \
    -H "Content-Type: application/json" \
    -X POST 'https://api.rollbar.com/api/1/deploy' \
    -d@- <<EOF
    {
        "environment": "production",
        "revision": "$(git log --pretty=format:'%h' -1)",
        "rollbar_name": "iba",
        "local_username": "root",
        "comment": "$(git log -1)",
        "status": "succeeded"
    }
EOF
echo "Deploy successful!!!"

