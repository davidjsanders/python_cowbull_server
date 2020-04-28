ifndef BUILD_NUMBER
  override BUILD_NUMBER := 20.04-41
endif

ifndef COWBULL_PORT
  override COWBULL_PORT := 5000
endif

ifndef COWBULL_SERVER
  override COWBULL_SERVER := localhost
endif

ifndef COWBULL_SERVER_URL
  override COWBULL_SERVER_URL := http://localhost
endif

ifndef GAE_BUCKET
  override GAE_BUCKET := the-bucket
endif

ifndef GAE_CREDENTIALS
  override GAE_CREDENTIALS := /tmp/keys/key.json
endif

ifndef GAE_PROJECT
  override GAE_PROJECT := the-project
endif

ifndef DATE_FORMAT
  override DATE_FORMAT := %Y-%m-%dT%H:%M:%S%Z
endif

ifndef HOMEDIR
  override HOMEDIR := $(shell echo ~)
endif

ifndef IMAGE_NAME
  override IMAGE_NAME := cowbull
endif

ifndef IMAGE_REG
  override IMAGE_REG := dsanderscan
endif

ifndef LOG_LEVEL
  override LOG_LEVEL := 30
endif

ifndef REDIS_IMAGE
  override REDIS_IMAGE := redis:alpine3.11
endif

ifndef REDIS_PORT
  override REDIS_PORT := 6379
endif

ifndef VENV
	override VENV := $(HOMEDIR)/virtuals/cowbull_p3/bin/activate
endif

ifndef WORKDIR
  override WORKDIR := $(shell dirname $(realpath $(lastword $(MAKEFILE_LIST))))
endif

define start_docker
	rm -f /tmp/start_docker.pid; \
	pid=$(shell docker run \
	  --detach \
	  -p $(REDIS_PORT):6379 \
	  $(REDIS_IMAGE)); \
	echo "Started Redis in container $$pid"
endef

define stop_docker
	echo; \
	echo -n "Stopping Redis container "; \
	docker stop $$pid; \
	echo -n "Removing Redis container "; \
	docker rm $$pid; \
	echo; \
	echo
endef

define end_log
	echo; \
	echo "Started $(1) at  : $(2)"; \
	echo "Finished $(1) at : $(3)"; \
	echo
endef

SHELL := /bin/bash
P_PERSISTER := '{"engine_name": "redis", "parameters": {"host": "localhost", "port": 6379, "db": 0, "password": ""}}'
# P_PERSISTER := '{"engine_name": "gcpdatastore", "parameters": {}}'

.PHONY: build cloudbuild cloudlocal cloudrun cloudstop curltest debug docker dump push run shell systest unittest

build:
	@start="`date +"$(DATE_FORMAT)"`"; \
	docker build \
	    --build-arg=build_number=$(BUILD_NUMBER) \
		--tag $(IMAGE_REG)/$(IMAGE_NAME):$(BUILD_NUMBER) \
		-f vendor/docker/Dockerfile \
		. ; \
	enddate="`date +$(DATE_FORMAT)`"; \
	$(call end_log,"build",$$start,$$enddate)

cloudbuild:
	@start="`date +"$(DATE_FORMAT)"`"; \
	gcloud builds submit --config=cloudbuild-google.yaml; \
	enddate="`date +$(DATE_FORMAT)`"; \
	$(call end_log,"build",$$start,$$enddate)

cloudlocal:
	@start="`date +"$(DATE_FORMAT)"`"; \
	docker run \
	    --name cowbull-server \
		--rm \
		-it \
	    -p 9090:8080 \
	    -e PERSISTER='{"engine_name": "gaestorage", "parameters":{"bucket": "$(GAE_BUCKET)", "credentials_file": "/tmp/keys/key.json", "project": "$(GAE_PROJECT)"}}' \
	    -e PORT=8080 \
	    -e GOOGLE_APPLICATION_CREDENTIALS=/tmp/keys/key.json \
		-v $(GAE_CREDENTIALS):/tmp/keys/key.json \
	    $(IMAGE_REG)/$(IMAGE_NAME):$(BUILD_NUMBER); \
	enddate="`date +$(DATE_FORMAT)`"; \
	$(call end_log,"build",$$start,$$enddate)
# 

cloudrun:
	@start="`date +"$(DATE_FORMAT)"`"; \
	gcloud run deploy cloudrun-make \
	  --image=$(IMAGE_REG)/$(IMAGE_NAME):$(BUILD_NUMBER) \
	  --allow-unauthenticated \
	  --set-env-vars "^;^PERSISTER='{\"engine_name\": \"file\", \"parameters\": {}}'" \
	  --set-env-vars LOGGING_LEVEL="10" \
	  --platform managed \
	  --region us-east1; \
	enddate="`date +$(DATE_FORMAT)`"; \
	$(call end_log,"build",$$start,$$enddate)

cloudstop:
	@start="`date +"$(DATE_FORMAT)"`"; \
	gcloud run services delete -q cloudrun-make --platform managed --region us-east1 ; \
	enddate="`date +$(DATE_FORMAT)`"; \
	$(call end_log,"build",$$start,$$enddate)

curltest:
	@start="`date +"$(DATE_FORMAT)"`"; \
	echo ""; \
	echo "List game modes"; \
	echo "---------------"; \
	curl $(COWBULL_SERVER_URL):$(COWBULL_PORT)/v1/modes ; \
	echo ; \
	echo ""; \
	echo "Get a game"; \
	echo "----------"; \
	curl $(COWBULL_SERVER_URL):$(COWBULL_PORT)/v1/game ; \
	echo ; \
	echo ; \
	enddate="`date +$(DATE_FORMAT)`"; \
	$(call end_log,"build",$$start,$$enddate)

debug:
	@start="`date +"$(DATE_FORMAT)"`"; \
	source $(VENV); \
	$(call start_docker,10); \
	PYTHONPATH=$(WORKDIR) \
		LOGGING_LEVEL=10 \
		PERSISTER=$(P_PERSISTER) \
		PORT=$(COWBULL_PORT) \
		FLASK_PORT=$(COWBULL_PORT) \
		FLASK_DEBUG=true \
		python main.py; \
	deactivate; \
	$(call stop_docker); \
	enddate="`date +$(DATE_FORMAT)`"; \
	$(call end_log,"debug",$$start,$$enddate)

docker:
	@start="`date +"$(DATE_FORMAT)"`"; \
	source $(VENV); \
	$(call start_docker,10); \
	docker run \
	  --name cowbull_server \
	  -it \
	  --rm \
	  -p $(COWBULL_PORT):8080 \
	  --env WORKERS=1 \
	  --env PORT=8080 \
	  --env LOGGING_LEVEL=$(LOG_LEVEL) \
	  --env PERSISTER=$(P_PERSISTER) \
	  $(IMAGE_REG)/$(IMAGE_NAME):$(BUILD_NUMBER); \
	$(call stop_docker); \
	enddate="`date +$(DATE_FORMAT)`"; \
	$(call end_log,"build",$$start,$$enddate)

dump:
	@start="`date +"$(DATE_FORMAT)"`"; \
	source $(VENV); \
	PYTHONPATH=$(WORKDIR) \
		LOGGING_LEVEL=$(LOG_LEVEL) \
	    WORKERS=1 \
		PERSISTER=$(P_PERSISTER) \
		PORT=$(COWBULL_PORT) \
		FLASK_PORT=$(COWBULL_PORT) \
		FLASK_DEBUG=true \
		COWBULL_DRY_RUN=true \
		python main.py; \
	deactivate; \
	enddate="`date +$(DATE_FORMAT)`"; \
	$(call end_log,"debug",$$start,$$enddate)

push:
	@start="`date +"$(DATE_FORMAT)"`"; \
	docker push $(IMAGE_REG)/$(IMAGE_NAME):$(BUILD_NUMBER); \
	enddate="`date +$(DATE_FORMAT)`"; \
	$(call end_log,"push",$$start,$$enddate)

#		PERSISTER='{"engine_name": "redis", "parameters": {"host": "localhost", "port": 6379, "db": 0, "password": ""}}' \

run:
	@start="`date +"$(DATE_FORMAT)"`"; \
	source $(VENV); \
	$(call start_docker,30); \
	PYTHONPATH=$(WORKDIR) \
	    FLASK_DEBUG=False \
		FLASK_ENV=run \
	    WORKERS=1 \
		LOGGING_LEVEL=$(LOG_LEVEL) \
		PERSISTER=$(P_PERSISTER) \
		PORT=$(COWBULL_PORT) \
		FLASK_PORT=$(COWBULL_PORT) \
		python main.py; \
	deactivate; \
	$(call stop_docker);  \
	enddate="`date +$(DATE_FORMAT)`"; \
	$(call end_log,"run",$$start,$$enddate)

shell:
	@start="`date +"$(DATE_FORMAT)"`"; \
	$(call start_docker,30); \
	docker run \
		-it --rm  \
		--name cowbull_server \
		-p $(COWBULL_PORT):8080 \
	    --env WORKERS=1 \
		--env PORT=8080 \
		--env LOGGING_LEVEL=$(LOG_LEVEL) \
		--env PERSISTER=$(P_PERSISTER) \
	    --entrypoint=/bin/sh \
		$(IMAGE_REG)/$(IMAGE_NAME):$(BUILD_NUMBER); \
	$(call stop_docker);  \
	enddate="`date +$(DATE_FORMAT)`"; \
	$(call end_log,"run",$$start,$$enddate)

systest:
	@start="`date +"$(DATE_FORMAT)"`"; \
	source $(VENV); \
	$(call start_docker,30); \
	PYTHONPATH=$(WORKDIR) \
		LOGGING_LEVEL=$(LOG_LEVEL) \
		PERSISTER=$(P_PERSISTER) \
		PORT=$(COWBULL_PORT) \
		python systests/main.py; \
	deactivate; \
	$(call stop_docker);  \
	enddate="`date +$(DATE_FORMAT)`"; \
	$(call end_log,"tests",$$start,$$enddate)

unittest:
	@start="`date +"$(DATE_FORMAT)"`"; \
	source $(VENV); \
	$(call start_docker,30); \
	PYTHONPATH=$(WORKDIR) \
		python unittests/main.py; \
	deactivate; \
	$(call stop_docker);  \
	enddate="`date +$(DATE_FORMAT)`"; \
	$(call end_log,"tests",$$start,$$enddate)
