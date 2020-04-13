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
COPY        . ./

RUN         pip3 install --upgrade pip
RUN         pip3 install -r /cowbull/image-requirements \
&&          pip install gunicorn==19.9.0

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