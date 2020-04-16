FROM        python:3.8.2-slim-buster
RUN         apt-get update \
            && apt-get upgrade -y
RUN         addgroup --gid 10000 cowbull_g \
            && adduser --uid 10000 --ingroup cowbull_g --disabled-password --home /cowbull --gecos "" cowbull \
            && chown cowbull /cowbull

ENV         APP_HOME    /cowbull
WORKDIR     $APP_HOME
COPY        image-requirements /cowbull/image-requirements

RUN         pip3 install --upgrade pip
RUN         pip3 install -r /cowbull/image-requirements \
&&          pip install gunicorn==19.9.0

COPY        . ./
USER        cowbull
ENV         PYTHONPATH="/cowbull"

USER        root
RUN         chmod +x \
                /cowbull/healthcheck/healthcheck.sh \
                /cowbull/healthcheck/liveness.sh \
                /cowbull/entrypoint.sh \
                /cowbull/entrypoint-cloudrun.sh
USER        cowbull

ENTRYPOINT [ "/cowbull/entrypoint.sh" ]
ARG         build_number=latest
ENV         BUILD_NUMBER=${build_number}
ENV         WORKERS=1

EXPOSE      8080
HEALTHCHECK \
    --interval=10s \
    --timeout=5s \
    --retries=3 \
    CMD [ "/bin/sh", "-c", "/cowbull/healthcheck/healthcheck.sh" ]

LABEL       MAINTAINER="dsanderscanada@gmail.com"