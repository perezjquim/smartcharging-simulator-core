# > CONSTANTS
PATTERN_BEGIN=»»»»»»»»»»»»»»»»»»»»»»»»»»»»»»»»»»»»»»»»»»»»»
PATTERN_END=«««««««««««««««««««««««««««««««««««««««««««««

BUILDPACK_BUILDER=heroku/buildpacks:18

SIMULATOR_NETWORK_NAME=net_energysim

SIMULATOR_PACK_NAME=pack_energysim_simulator
SIMULATOR_CONTAINER_NAME=cont_energysim_simulator
SIMULATOR_HOST=0.0.0.0
SIMULATOR_FLASK_PORT=9000
SIMULATOR_FLASK_PORT_EXTERNAL=9001:9000
SIMULATOR_WS_PORT=9001
SIMULATOR_WS_PORT_EXTERNAL=9002:9001

GATEWAY_HOST=cont_energysim_gateway
GATEWAY_PORT=8000
# < CONSTANTS

main: stop-docker-simulator run-docker-simulator

# > DOCKER-SIMULATOR
run-docker-simulator: build-docker-simulator start-docker-simulator

build-docker-simulator:
	@echo '$(PATTERN_BEGIN) BUILDING SIMULATOR PACK...'

	@if [ pip list | grep -F pipreqs ]; then echo "pipreqs already installed!" ;\
	else echo "pipreqs not installed! installing..." && pip install pipreqs

	@pipreqs --force --savepath requirements.txt.tmp
	@sort -r requirements.txt.tmp > requirements.txt.tmp.sorted
	@if cmp -s requirements.txt.tmp.sorted requirements.txt; then :;\
	else cp -f requirements.txt.tmp.sorted requirements.txt; fi
	@rm -f requirements.txt.tmp
	@rm -f requirements.txt.tmp.sorted
	
	@pack build $(SIMULATOR_PACK_NAME) \
	--builder $(BUILDPACK_BUILDER) \
	--pull-policy if-not-present \
	--verbose

	@echo '$(PATTERN_END) SIMULATOR PACK BUILT!'

start-docker-simulator:
	@echo '$(PATTERN_BEGIN) STARTING SIMULATOR PACK...'

	@docker run -d \
	--name $(SIMULATOR_CONTAINER_NAME) \
	--network $(SIMULATOR_NETWORK_NAME) \
	-p $(SIMULATOR_FLASK_PORT_EXTERNAL) \
	-p $(SIMULATOR_WS_PORT_EXTERNAL) \
	-e SIMULATOR_HOST=$(SIMULATOR_HOST) \
	-e SIMULATOR_WS_PORT=$(SIMULATOR_WS_PORT) \
	$(SIMULATOR_PACK_NAME)
	
	@echo '$(PATTERN_END) SIMULATOR PACK STARTED!'

stop-docker-simulator:
	@echo '$(PATTERN_BEGIN) STOPPING SIMULATOR PACK...'

	@( docker rm -f $(SIMULATOR_CONTAINER_NAME) ) || true

	@echo '$(PATTERN_END) SIMULATOR PACK STOPPED!'	
# < DOCKER-SIMULATOR

# > SIMULATOR
run-simulator: prep-simulator start-simulator

prep-simulator:
	@until nc -z $(GATEWAY_HOST) $(GATEWAY_PORT); do \
	echo "$$(date) - waiting for gateway..."; \
	sleep 2; \
	done

start-simulator:
	@FLASK_APP=simulator/main.py \
	python3 -m flask run \
	--host=$(SIMULATOR_HOST) \
	--port=$(SIMULATOR_FLASK_PORT)
# < SIMULATOR