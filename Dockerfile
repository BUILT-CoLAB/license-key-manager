FROM python:3.10.7-alpine3.16

RUN apk add bash curl gcc libc-dev libffi-dev 
RUN apk add sqlite

RUN pip3 install greenlet==1.1.2 gunicorn==20.1.0 gevent==21.12.0 

# Create a group and user
RUN addgroup -S appgroup && adduser -S appuser -G appgroup


WORKDIR /license-manager

COPY requirements.txt requirements.txt
RUN pip3 install --no-cache-dir -r requirements.txt

COPY --chown=appuser ./bin /license-manager/bin
COPY --chown=appuser .env /license-manager/bin

RUN chown -R appuser:appgroup /license-manager/bin/database

ARG DEFAULT_WORKERS=2
ARG DEFAULT_THREADS=4
ARG DEFAULT_PORT=8000

ENV WORKERS=${DEFAULT_WORKERS}
ENV THREADS=${DEFAULT_THREADS}
ENV PORT=${DEFAULT_PORT}

EXPOSE ${PORT}

RUN set FLASK_RUN_PORT=${PORT}
RUN set FLASK_ENV=production

HEALTHCHECK --interval=15m --timeout=5s \
    CMD curl --fail http://localhost:${PORT} || exit 1     

# Tell docker that all future commands should run as the appuser user
USER appuser

CMD ["bash", "-c", "gunicorn -w ${WORKERS} --threads ${THREADS} -b :${PORT} -k gevent --preload 'bin:create_app()'"]