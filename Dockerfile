ARG PYTHON_VERSION=3.11-slim-bullseye

FROM python:${PYTHON_VERSION}

# Install Node.js for Tailwind CSS
RUN apt-get update && apt-get install -y curl \
    && curl -fsSL https://deb.nodesource.com/setup_18.x | bash - \
    && apt-get install -y nodejs \
    && rm -rf /var/lib/apt/lists/*

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV FLY_APP_NAME=pamplesneak

# install psycopg2 dependencies.
RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

RUN mkdir -p /code

WORKDIR /code

COPY requirements-deploy.txt /tmp/requirements.txt
RUN set -ex && \
    pip install --upgrade pip && \
    pip install -r /tmp/requirements.txt && \
    rm -rf /root/.cache/
COPY . /code

# Install Tailwind CSS and build styles
RUN python3 manage.py tailwind install --no-input
RUN python3 manage.py tailwind build --no-input

RUN python3 manage.py collectstatic --noinput

EXPOSE 8000

# CMD ["gunicorn", "--bind", ":8000", "--workers", "2", "pamplesneak.wsgi"]
CMD ["daphne", "-b", "0.0.0.0", "-p", "8000", "pamplesneak.asgi:application"]


# RUN python3 wordbank_converter.py     
# RUN python3 manage.py loaddata data/examplewords.json
