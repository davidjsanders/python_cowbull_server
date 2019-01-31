FROM        python:3.5.3-slim
MAINTAINER  David Sanders
RUN         apt-get update && \
            && groupadd -r cowbull_g \
            && mkdir /cowbull \
            && useradd -r -G cowbull_g -d /cowbull cowbull \
            && chown cowbull /cowbull \
            && apt-get install --yes \
                libgcrypt20=1.6.3-2+deb8u5 \
                openssl=1.0.1t-1+deb8u10 \
                procps=2:3.3.9-9+deb8u1 \
                systemd=215-17+deb8u8
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
COPY        *.py  /cowbull/
COPY        LICENSE /cowbull/
CMD         ["gunicorn", "-b", "0.0.0.0:8080", "-w", "4", "app:app"]
EXPOSE      8080
