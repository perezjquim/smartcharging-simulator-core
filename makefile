# > CONSTANTS
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
# < CONSTANTS

main: run-docker-rabbit run-docker-gateway

# > RABBIT
run-docker-rabbit: stop-docker-rabbit start-docker-rabbit

start-docker-rabbit:
	@echo '$(PATTERN_BEGIN) STARTING RABBIT...'
	@( docker network create $(RABBIT_NETWORK_NAME) || true )
	@docker run -d --name $(RABBIT_CONTAINER_NAME) --network $(RABBIT_NETWORK_NAME) -e RABBITMQ_DEFAULT_USER=$(RABBIT_USER) -e RABBITMQ_DEFAULT_PASS=$(RABBIT_PASSWORD) -p $(RABBIT_MANAGEMENT_PORTS) $(RABBIT_IMAGE_NAME)
	@echo '$(PATTERN_END) RABBIT STARTED!'	

stop-docker-rabbit:
	@echo '$(PATTERN_BEGIN) STOPPING RABBIT...'
	@( docker stop $(RABBIT_CONTAINER_NAME) && docker rm $(RABBIT_CONTAINER_NAME) ) || true
	@echo '$(PATTERN_END) RABBIT STOPPED!'	
# < RABBIT

# > GATEWAY
run-docker-gateway: stop-pack-gateway prep-pack-gateway build-pack-gateway start-pack-gateway

prep-pack-gateway:
	@echo '$(PATTERN_BEGIN) PREPARING GATEWAY PACK...'
	@pipreqs ./ --force
	@pack set-default-builder $(BUILDPACK_BUILDER)
	@echo '$(PATTERN_END) GATEWAY PACK READY!'

build-pack-gateway:
	@echo '$(PATTERN_BEGIN) BUILDING GATEWAY PACK...'
	@pack build --network $(RABBIT_NETWORK_NAME) $(BUILDPACK_NAME)
	@echo '$(PATTERN_END) GATEWAY PACK BUILT!'

start-pack-gateway:
	@echo '$(PATTERN_BEGIN) STARTING GATEWAY PACK...'
	@( docker network create $(RABBIT_NETWORK_NAME) || true )
	@docker run -d --name $(BUILDPACK_NAME) --network $(RABBIT_NETWORK_NAME) -e RABBIT_USER=$(RABBIT_USER) -e RABBIT_PASSWORD=$(RABBIT_PASSWORD) -e RABBIT_HOST=$(RABBIT_CONTAINER_NAME) -e RABBIT_MANAGEMENT_PORT=$(RABBIT_MANAGEMENT_PORT) -e RABBIT_PORT=$(RABBIT_PORT) -p $(GATEWAY_PORTS) $(BUILDPACK_NAME)
	@echo '$(PATTERN_END) GATEWAY PACK STARTED!'

stop-pack-gateway:
	@echo '$(PATTERN_BEGIN) STOPPING GATEWAY PACK...'
	@( docker stop $(BUILDPACK_NAME) && docker rm $(BUILDPACK_NAME) ) || true
	@echo '$(PATTERN_END) GATEWAY PACK STOPPED!'	
# < GATEWAY

# > NAMEKO
run-nameko: prep-nameko start-nameko

prep-nameko:
	@until nc -z $(RABBIT_CONTAINER_NAME) $(RABBIT_PORT); do echo "$$(date) - waiting for rabbitmq..."; sleep 2; done

start-nameko:
	@nameko run --config nameko-config.yml gateway.service --backdoor $(GATEWAY_BACKDOOR)
# < NAMEKO