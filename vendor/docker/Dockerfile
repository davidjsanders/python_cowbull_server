FROM        python:3.6-alpine
MAINTAINER  David Sanders
RUN         apk update \
            && addgroup -g 10000 cowbull_g \
            && mkdir /cowbull \
            && adduser -u 10000 -G cowbull_g --disabled-password --home /cowbull cowbull \
            && chown cowbull /cowbull \
            && apk add curl
WORKDIR     /cowbull
COPY        requirements.txt /cowbull
RUN         pip install -q setuptools
RUN         pip install -q -r /cowbull/requirements.txt

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

USER        root
RUN         chmod +x \
                /cowbull/healthcheck/healthcheck.sh \
                /cowbull/healthcheck/liveness.sh
USER        cowbull

CMD         ["gunicorn", "-b", "0.0.0.0:8080", "-w", "4", "app:app"]
EXPOSE      8080
HEALTHCHECK \
    --interval=10s \
    --timeout=5s \
    --start-period=5s \
    --retries=3 \
    CMD [ "/bin/sh", "-c", "/cowbull/healthcheck/healthcheck.sh" ]
LABEL       MAINTAINER="dsanderscanada@gmail.com"