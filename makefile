# > CONSTANTS
PATTERN_BEGIN=»»»»»»»»»»»»»»»»»»»»»»»»»»»»»»»»»»»»»»»»»»»»»
PATTERN_END=«««««««««««««««««««««««««««««««««««««««««««««

BUILDPACK_BUILDER=heroku/buildpacks:18

GATEWAY_PACK_NAME=pack_energysim_gateway
GATEWAY_CONTAINER_NAME=cont_energysim_gateway
GATEWAY_BACKDOOR=3000
GATEWAY_PORTS=8003:8000

RABBIT_NETWORK_NAME=net_rabbitmq
RABBIT_CONTAINER_NAME=cont_energysim_rabbitmq
RABBIT_IMAGE_NAME=rabbitmq:3.7-management
RABBIT_USER=guest
RABBIT_PASSWORD=guest
RABBIT_PORT=5672
RABBIT_MANAGEMENT_PORT=15672
RABBIT_MANAGEMENT_PORTS=15673:15672
# < CONSTANTS

main: stop-docker-gateway stop-docker-rabbit start-docker-rabbit run-docker-gateway

# > RABBIT
start-docker-rabbit:
	@echo '$(PATTERN_BEGIN) STARTING RABBIT...'

	@( docker network create $(RABBIT_NETWORK_NAME) || true )
	@docker run -d \
	--name $(RABBIT_CONTAINER_NAME) \
	--network $(RABBIT_NETWORK_NAME) \
	-e RABBIT_DEFAULT_USER=$(RABBIT_USER) \
	-e RABBIT_DEFAULT_PASS=$(RABBIT_PASSWORD) \
	-p $(RABBIT_MANAGEMENT_PORTS) \
	$(RABBIT_IMAGE_NAME) 

	@echo '$(PATTERN_END) RABBIT STARTED!'	

stop-docker-rabbit:
	@echo '$(PATTERN_BEGIN) STOPPING RABBIT...'

	@( docker stop $(RABBIT_CONTAINER_NAME) && docker rm $(RABBIT_CONTAINER_NAME) ) || true
	@( docker network remove $(RABBIT_NETWORK_NAME) || true )

	@echo '$(PATTERN_END) RABBIT STOPPED!'	
# < RABBIT

# > GATEWAY
run-docker-gateway: build-docker-gateway start-docker-gateway

build-docker-gateway:
	@echo '$(PATTERN_BEGIN) BUILDING GATEWAY PACK...'

	@pipreqs ./ --force
	@pack build $(GATEWAY_PACK_NAME) \
	--builder $(BUILDPACK_BUILDER)

	@echo '$(PATTERN_END) GATEWAY PACK BUILT!'

start-docker-gateway:
	@echo '$(PATTERN_BEGIN) STARTING GATEWAY PACK...'

	@docker run -d \
	--name $(GATEWAY_CONTAINER_NAME) \
	--network $(RABBIT_NETWORK_NAME) \
	-e RABBIT_USER=$(RABBIT_USER) \
	-e RABBIT_PASSWORD=$(RABBIT_PASSWORD) \
	-e RABBIT_HOST=$(RABBIT_CONTAINER_NAME) \
	-e RABBIT_MANAGEMENT_PORT=$(RABBIT_MANAGEMENT_PORT) \
	-e RABBIT_PORT=$(RABBIT_PORT) \
	-p $(GATEWAY_PORTS) \
	$(GATEWAY_PACK_NAME)
	
	@echo '$(PATTERN_END) GATEWAY PACK STARTED!'

stop-docker-gateway:
	@echo '$(PATTERN_BEGIN) STOPPING GATEWAY PACK...'

	@( docker stop $(GATEWAY_CONTAINER_NAME) && docker rm $(GATEWAY_CONTAINER_NAME) ) || true

	@echo '$(PATTERN_END) GATEWAY PACK STOPPED!'	
# < GATEWAY

# > NAMEKO
run-nameko-gateway: prep-nameko-gateway start-nameko-gateway

prep-nameko-gateway:
	@until nc -z $(RABBIT_CONTAINER_NAME) $(RABBIT_PORT); do \
	echo "$$(date) - waiting for rabbitmq..."; \
	sleep 2; \
	done

start-nameko-gateway:
	@nameko run gateway.service \
	--config nameko-config.yml  \
	--backdoor $(GATEWAY_BACKDOOR)
# < NAMEKO