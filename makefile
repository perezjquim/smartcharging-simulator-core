# > CONSTANTS
PATTERN_BEGIN=»»»»»»»»»»»»»»»»»»»»»»»»»»»»»»»»»»»»»»»»»»»»»
PATTERN_END=«««««««««««««««««««««««««««««««««««««««««««««

BUILDPACK_BUILDER=heroku/buildpacks:18

SIMULATOR_NETWORK_NAME=net_energysim

SIMULATOR_PACK_NAME=pack_energysim_simulator
SIMULATOR_CONTAINER_NAME=cont_energysim_simulator
SIMULATOR_PORT=7777

SIMULATOR_FLASK_HOST=0.0.0.0
SIMULATOR_FLASK_PORT=6666
# < CONSTANTS

main: stop-docker-simulator run-docker-simulator

# > DOCKER-SIMULATOR
run-docker-simulator: build-docker-simulator start-docker-simulator

build-docker-simulator:
	@echo '$(PATTERN_BEGIN) BUILDING SIMULATOR PACK...'

	@pipreqs --force --savepath requirements.txt.tmp
	@sort -r requirements.txt.tmp > requirements.txt.tmp.sorted
	@if cmp -s requirements.txt.tmp.sorted requirements.txt; then :;\
	else cp -f requirements.txt.tmp.sorted requirements.txt; fi
	@rm -f requirements.txt.tmp
	@rm -f requirements.txt.tmp.sorted
	
	@pack build $(SIMULATOR_PACK_NAME) \
	--builder $(BUILDPACK_BUILDER)

	@echo '$(PATTERN_END) SIMULATOR PACK BUILT!'

start-docker-simulator:
	@echo '$(PATTERN_BEGIN) STARTING SIMULATOR PACK...'

	@docker run -d \
	--name $(SIMULATOR_CONTAINER_NAME) \
	--network $(SIMULATOR_NETWORK_NAME) \
	-p $(SIMULATOR_PORT) \
	$(SIMULATOR_PACK_NAME)
	
	@echo '$(PATTERN_END) SIMULATOR PACK STARTED!'

stop-docker-simulator:
	@echo '$(PATTERN_BEGIN) STOPPING SIMULATOR PACK...'

	@( docker stop $(SIMULATOR_CONTAINER_NAME) && docker rm $(SIMULATOR_CONTAINER_NAME) ) || true

	@echo '$(PATTERN_END) SIMULATOR PACK STOPPED!'	
# < DOCKER-SIMULATOR

# > SIMULATOR
run-simulator:
	@FLASK_APP=simulator/main.py \
	python3 -m flask run \
	--host=$(SIMULATOR_FLASK_HOST) \
	--port=$(SIMULATOR_FLASK_PORT)
# < SIMULATOR