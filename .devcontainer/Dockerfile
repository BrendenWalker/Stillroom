# Official Debian Python image (glibc). Cursor's remote server needs bash, wget, curl, and tar.
FROM python:3.13-bookworm

ENV PYTHONUNBUFFERED=1

EXPOSE 8000
EXPOSE 8080

RUN apt-get update && export DEBIAN_FRONTEND=noninteractive \
    && apt-get install -y --no-install-recommends \
        bash \
        wget \
        curl \
        tar \
        ca-certificates \
        git \
        openssh-client \
        postgresql-client \
        libpq-dev \
        gettext \
        libjpeg62-turbo-dev \
        libwebp-dev \
        zlib1g-dev \
        libxml2-dev \
        libxslt1-dev \
        libxmlsec1-dev \
        libxmlsec1-openssl \
        libldap2-dev \
        libsasl2-dev \
        libssl-dev \
        libffi-dev \
        pkg-config \
        gcc \
        g++ \
    && curl -fsSL https://deb.nodesource.com/setup_22.x | bash - \
    && apt-get install -y --no-install-recommends nodejs \
    && corepack enable \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /tmp/pip-tmp/
RUN python -m pip install --upgrade pip \
    && pip install wheel==0.45.1 \
    && pip install -r /tmp/pip-tmp/requirements.txt --no-cache-dir \
    && rm -rf /tmp/pip-tmp
