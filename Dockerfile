FROM python:3.10.5-alpine3.16

RUN apk add bash curl gcc libc-dev libffi-dev 
RUN pip3 install gunicorn gevent 

# Create a group and user
RUN addgroup -S appgroup && adduser -S appuser -G appgroup
# Tell docker that all future commands should run as the appuser user
USER appuser

WORKDIR /license-manager

COPY requirements.txt requirements.txt
RUN pip3 install --no-cache-dir -r requirements.txt

COPY ./bin /license-manager/bin
COPY .env /license-manager/bin

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

CMD ["bash", "-c", "gunicorn -w ${WORKERS} --threads ${THREADS} -b :${PORT} -k gevent --preload 'bin:create_app()'"]