FROM nginx/unit:1.25.0-python3.9
ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1

WORKDIR /backend
COPY requirements.txt /backend/
RUN apt update && apt install -y python3-pip                                  \
    && pip3 install -r requirements.txt                                       \
    && apt remove -y python3-pip                                              \
    && apt autoremove --purge -y                                              \
    && rm -rf /var/lib/apt/lists/* /etc/apt/sources.list.d/*.list
COPY unit_config.json /docker-entrypoint.d/
COPY entrypoint.sh /docker-entrypoint.d/
RUN chmod 755 /docker-entrypoint.d/entrypoint.sh
COPY . /backend/
RUN DJANGO_SECRET_KEY=empty YANDEX_GEOCODER_APIKEY=empty python manage.py collectstatic --noinput
EXPOSE 80
