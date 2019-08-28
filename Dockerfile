FROM        python:3.7.4-alpine3.10
MAINTAINER  David Sanders
RUN         apk update \
            && addgroup -g 10000 cowbull_g \
            && mkdir /cowbull \
            && adduser -u 10000 -G cowbull_g --disabled-password --home /cowbull cowbull \
            && chown cowbull /cowbull \
            && apk add \
                curl \
            && curl -Lo /tmp/curl-7.65.3-r0.apk http://dl-3.alpinelinux.org/alpine/edge/main/x86_64/curl-7.65.3-r0.apk \
            && apk add /tmp/curl-7.65.3-r0.apk \
            && curl -Lo /tmp/musl-1.1.23-r3.apk http://dl-3.alpinelinux.org/alpine/edge/main/x86_64/musl-1.1.23-r3.apk \
            && apk add /tmp/musl-1.1.23-r3.apk
WORKDIR     /cowbull
COPY        requirements.txt /cowbull
RUN         pip install -q setuptools \
            && pip install -q -r /cowbull/requirements.txt

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

USER        root
RUN         chmod +x \
                /cowbull/healthcheck/healthcheck.sh \
                /cowbull/healthcheck/liveness.sh \
                /cowbull/entrypoint.sh
USER        cowbull

ENTRYPOINT [ "/cowbull/entrypoint.sh" ]
EXPOSE      8080
HEALTHCHECK \
    --interval=10s \
    --timeout=5s \
    --retries=3 \
    CMD [ "/bin/sh", "-c", "/cowbull/healthcheck/healthcheck.sh" ]

LABEL       MAINTAINER="dsanderscanada@gmail.com"