FROM python:3.9-alpine

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

WORKDIR /app
COPY Pipfile* ./

# https://stackoverflow.com/questions/41574928/psycopg2-installation-for-python2-7-alpine-in-docker
RUN apk update && apk add libpq

RUN set -ex \
    && apk add --no-cache --virtual .build-deps \
            gcc \
            make \
            libc-dev \
            musl-dev \
            linux-headers \
            pcre-dev \
            postgresql-dev \
            zlib-dev \
            jpeg-dev \
            python3-dev \
            openssl-dev \
            openssl \
            libffi-dev \
            rust \
            cargo

RUN pip3 install --upgrade pipenv \
    && LIBRARY_PATH=/lib:/usr/lib /bin/sh -c "pipenv sync --clear" \
    && runDeps="$( \
            scanelf --needed --nobanner --recursive .venv \
                    | awk '{ gsub(/,/, "\nso:", $2); print "so:" $2 }' \    
                    | sort -u \
                    | xargs -r apk info --installed \
                    | sort -u \
    )" \
    && apk del .build-deps \
    && apk add --no-cache $runDeps

RUN pipenv install

COPY . .

RUN mkdir /app/server/ipfs_files
RUN chmod +x -R scripts/

# Django settings module
ENV DJANGO_SETTINGS_MODULE="server.settings"

CMD ["./scripts/start-server.sh"]