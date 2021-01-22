PATTERN_BEGIN=>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
PATTERN_END=<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<

BUILDPACK_BUILDER=heroku/buildpacks:18
BUILDPACK_NAME=cont_sim_gateway
GATEWAY_BACKDOOR=3000
GATEWAY_PORTS=8003:8000

RABBIT_NETWORK_NAME=net_rabbit
RABBIT_CONTAINER_NAME=cont_sim_rabbitmq
RABBIT_IMAGE_NAME=rabbitmq:3.7-management
RABBIT_USER=guest
RABBIT_PASSWORD=guest
RABBIT_PORT=5672
RABBIT_MANAGEMENT_PORT=15672
RABBIT_MANAGEMENT_PORTS=15673:15672

deploy: prep-pack build-pack run-docker

test: setup run-nameko

# > RABBIT
run-rabbit: stop-rabbit start-rabbit

start-rabbit:
	@echo '$(PATTERN_BEGIN) RUNNING...'
	@( docker network create $(RABBIT_NETWORK_NAME) || true )
	@docker run -d --name $(RABBIT_CONTAINER_NAME) --network $(RABBIT_NETWORK_NAME) -e RABBITMQ_DEFAULT_USER=$(RABBIT_USER) -e RABBITMQ_DEFAULT_PASS=$(RABBIT_PASSWORD) -p $(RABBIT_MANAGEMENT_PORTS) $(RABBIT_IMAGE_NAME)
	@echo '$(PATTERN_END) RUN COMPLETE!'	

stop-rabbit:
	@echo '$(PATTERN_BEGIN) STOPPING...'
	@( docker stop $(RABBIT_CONTAINER_NAME) && docker rm $(RABBIT_CONTAINER_NAME) ) || true
	@echo '$(PATTERN_END) STOPPED!'	
# < RABBIT

# > PACK
prep-pack:
	@echo '$(PATTERN_BEGIN) PREPARING...'
	@pipreqs ./ --force
	@pack set-default-builder $(BUILDPACK_BUILDER)
	@echo '$(PATTERN_END) PREPARED!'

build-pack:
	@echo '$(PATTERN_BEGIN) BUILDING...'
	@pack build --network $(RABBIT_NETWORK_NAME) $(BUILDPACK_NAME)
	@echo '$(PATTERN_END) BUILD COMPLETE!'
# < PACK

# > DOCKER
run-docker: stop-docker start-docker

start-docker:
	@echo '$(PATTERN_BEGIN) RUNNING...'
	@( docker network create $(RABBIT_NETWORK_NAME) || true )
	@docker run -d --name $(BUILDPACK_NAME) --network $(RABBIT_NETWORK_NAME) -e RABBIT_USER=$(RABBIT_USER) -e RABBIT_PASSWORD=$(RABBIT_PASSWORD) -e RABBIT_HOST=$(RABBIT_CONTAINER_NAME) -e RABBIT_MANAGEMENT_PORT=$(RABBIT_MANAGEMENT_PORT) -e RABBIT_PORT=$(RABBIT_PORT) -p $(GATEWAY_PORTS) $(BUILDPACK_NAME)
	@echo '$(PATTERN_END) RUN COMPLETE!'

stop-docker:
	@echo '$(PATTERN_BEGIN) STOPPING...'
	@( docker stop $(BUILDPACK_NAME) ; docker rm $(BUILDPACK_NAME) ) || true
	@echo '$(PATTERN_END) STOPPED!'	
# < DOCKER

# > NAMEKO
run-nameko: prep-nameko start-nameko

prep-nameko:
	@until nc -z $(RABBIT_CONTAINER_NAME) $(RABBIT_PORT); do echo "$$(date) - waiting for rabbitmq..."; sleep 2; done

start-nameko:
	@nameko run --config nameko-config.yml gateway.service --backdoor $(GATEWAY_BACKDOOR)
# < NAMEKO