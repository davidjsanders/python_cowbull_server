FROM        alpine:3.10.2
RUN         apk update \
            && addgroup -g 10000 cowbull_g \
            && mkdir /cowbull \
            && adduser -u 10000 -G cowbull_g --disabled-password --home /cowbull cowbull \
            && chown cowbull /cowbull \
            && apk add --update \
                curl \
                musl \
                python3 \
                py3-pip

ENV         APP_HOME    /cowbull
WORKDIR     $APP_HOME
COPY        image-requirements ./requirements.txt

RUN         pip3 install --upgrade pip
RUN         pip3 install -r /cowbull/requirements.txt \
&&          pip install gunicorn==19.9.0

USER        cowbull
ENV         PYTHONPATH="/cowbull"
COPY        extensions /cowbull/extensions/
COPY        flask_controllers /cowbull/flask_controllers/
COPY        flask_helpers /cowbull/flask_helpers
COPY        Game    /cowbull/Game/
COPY        Persistence /cowbull/Persistence/
COPY        PersistenceExtensions /cowbull/PersistenceExtensions/
COPY        python_cowbull_server /cowbull/python_cowbull_server/
COPY        Routes /cowbull/Routes
COPY        unittests /cowbull/unittests
COPY        systests /cowbull/systests
COPY        healthcheck /cowbull/healthcheck/
COPY        *.py  /cowbull/
COPY        LICENSE /cowbull/
COPY        entrypoint.sh /cowbull/
COPY        entrypoint-cloudrun.sh /cowbull/

USER        root
RUN         chmod +x \
                /cowbull/healthcheck/healthcheck.sh \
                /cowbull/healthcheck/liveness.sh \
                /cowbull/entrypoint.sh \
                /cowbull/entrypoint-cloudrun.sh
USER        cowbull

ENTRYPOINT [ "/cowbull/entrypoint.sh" ]
#CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 app:app
EXPOSE      8080
HEALTHCHECK \
    --interval=10s \
    --timeout=5s \
    --retries=3 \
    CMD [ "/bin/sh", "-c", "/cowbull/healthcheck/healthcheck.sh" ]

LABEL       MAINTAINER="dsanderscanada@gmail.com"