ifndef BUILD_NUMBER
  override BUILD_NUMBER := 20.04-8
endif

ifndef COWBULL_PORT
  override COWBULL_PORT := 8000
endif

ifndef COWBULL_SERVER
  override COWBULL_SERVER := localhost
endif

ifndef COWBULL_SERVER_IMAGE
  override COWBULL_SERVER_IMAGE := dsanderscan/cowbull:20.03-2
endif

ifndef COWBULL_WEBAPP_PORT
  override COWBULL_WEBAPP_PORT := 8080
endif

ifndef DATE_FORMAT
  override DATE_FORMAT := %Y-%m-%dT%H:%M:%S%Z
endif

ifndef HOMEDIR
  override HOMEDIR := $(shell echo ~)
endif

ifndef HOST_IF
  override HOST_IF := en3
endif

ifndef HOST_IP
  override HOST_IP := $(shell ipconfig getifaddr $(HOST_IF))
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
	docker run \
	  --detach \
	  --name redis \
	  -p $(REDIS_PORT):6379 \
	  $(REDIS_IMAGE)
endef

define stop_docker
	echo; \
	echo "Stopping Redis container "; \
	docker stop redis; \
	echo "Removing Redis container"; \
	docker rm redis; \
	echo; \
	echo
endef

define end_log
	echo; \
	echo "Started $(1) at  : $(2)"; \
	echo "Finished $(1) at : $(3)"; \
	echo
endef

.PHONY: build curltest debug docker dump push run shell systest unittest

build:
	@start="`date +"$(DATE_FORMAT)"`"; \
	docker build \
	    --build-arg=build_number=$(BUILD_NUMBER) \
		--tag $(IMAGE_REG)/$(IMAGE_NAME):$(BUILD_NUMBER) \
		-f vendor/docker/Dockerfile \
		. ; \
	enddate="`date +$(DATE_FORMAT)`"; \
	$(call end_log,"build",$$start,$$enddate)

curltest:
	@start="`date +"$(DATE_FORMAT)"`"; \
	echo ""; \
	echo "List game modes"; \
	echo "---------------"; \
	curl localhost:8000/v1/modes ; \
	echo ; \
	echo ""; \
	echo "Get a game"; \
	echo "----------"; \
	curl localhost:8000/v1/game ; \
	echo ; \
	echo ; \
	enddate="`date +$(DATE_FORMAT)`"; \
	$(call end_log,"build",$$start,$$enddate)

debug:
	@start="`date +"$(DATE_FORMAT)"`"; \
	source $(VENV); \
	$(call start_docker,10); \
	PYTHONPATH=$(WORKDIR) \
		LOGGING_LEVEL=$(LOG_LEVEL) \
		PERSISTER='{"engine_name": "redis", "parameters": {"host": "localhost", "port": 6379, "db": 0, "password": ""}}' \
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
	  --env PORT=8080 \
	  --env LOGGING_LEVEL=$(LOG_LEVEL) \
	  --env PERSISTER='{"engine_name": "redis", "parameters": {"host": "$(HOST_IP)", "port": 6379, "db": 0}}' \
	  $(IMAGE_REG)/$(IMAGE_NAME):$(BUILD_NUMBER); \
	$(call stop_docker); \
	enddate="`date +$(DATE_FORMAT)`"; \
	$(call end_log,"build",$$start,$$enddate)

dump:
	@start="`date +"$(DATE_FORMAT)"`"; \
	source $(VENV); \
	PYTHONPATH=$(WORKDIR) \
		LOGGING_LEVEL=$(LOG_LEVEL) \
		PERSISTER='{"engine_name": "redis", "parameters": {"host": "localhost", "port": 6379, "db": 0, "password": ""}}' \
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

run:
	@start="`date +"$(DATE_FORMAT)"`"; \
	source $(VENV); \
	$(call start_docker,30); \
	PYTHONPATH=$(WORKDIR) \
	    FLASK_DEBUG=False \
		FLASK_ENV=run \
		LOGGING_LEVEL=$(LOG_LEVEL) \
		PERSISTER='{"engine_name": "redis", "parameters": {"host": "localhost", "port": 6379, "db": 0, "password": ""}}' \
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
		--env PORT=8080 \
		--env LOGGING_LEVEL=$(LOG_LEVEL) \
		--env PERSISTER='{"engine_name": "redis", "parameters": {"host": "$(HOST_IP)", "port": 6379, "db": 0}}' \
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
		PERSISTER='{"engine_name": "redis", "parameters": {"host": "localhost", "port": 6379, "db": 0, "password": ""}}' \
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
		LOGGING_LEVEL=$(LOG_LEVEL) \
		python unittests/main.py; \
	deactivate; \
	$(call stop_docker);  \
	enddate="`date +$(DATE_FORMAT)`"; \
	$(call end_log,"tests",$$start,$$enddate)
