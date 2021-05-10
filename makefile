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

DB_VOLUME_NAME=vol_energysim
DB_PATH=/app/vol
DB_VOLUME=$(DB_VOLUME_NAME):$(DB_PATH)
DB_VOLUME_BACKUP=$(DB_VOLUME_NAME)_BACKUP
DB_VOLUME_BACKUP_FILENAME=$(DB_VOLUME_BACKUP).tar

UNIX_SUPRESS_OUTPUT=> /dev/null 2>&1
# < CONSTANTS

main: check-dependencies stop-docker-simulator run-docker-simulator

check-dependencies:
	@echo '$(PATTERN_BEGIN) CHECKING DEPENDENCIES...'

	@if ( pip3 list | grep -F pipreqs $(UNIX_SUPRESS_OUTPUT) ) ; then \
		echo "pipreqs already installed!" ; \
	else \
		echo "pipreqs not installed! installing..." && pip3 install pipreqs; \
	fi	

	@if ( dpkg -l pack-cli $(UNIX_SUPRESS_OUTPUT) ) ; then \
		echo "pack already installed!" ; \
	else \
		echo "pack not installed! please install..."; \
		exit 1; \
	fi			

	@bash -c 'source ~/.profile'		

	@echo '$(PATTERN_END) DEPENDENCIES CHECKED!'

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
	--builder $(BUILDPACK_BUILDER) \
	--pull-policy if-not-present \
	--verbose

	@echo '$(PATTERN_END) SIMULATOR PACK BUILT!'

start-docker-simulator:
	@echo '$(PATTERN_BEGIN) STARTING SIMULATOR PACK...'

	@docker run -d \
	--rm \
	--name $(SIMULATOR_CONTAINER_NAME) \
	--network $(SIMULATOR_NETWORK_NAME) \
	--volume $(DB_VOLUME) \
	-p $(SIMULATOR_FLASK_PORT_EXTERNAL) \
	-p $(SIMULATOR_WS_PORT_EXTERNAL) \
	-e SIMULATOR_HOST=$(SIMULATOR_HOST) \
	-e SIMULATOR_WS_PORT=$(SIMULATOR_WS_PORT) \
	-e FLASK_APP=simulator/main.py \
	$(SIMULATOR_PACK_NAME)
	
	@echo '$(PATTERN_END) SIMULATOR PACK STARTED!'

stop-docker-simulator:
	@echo '$(PATTERN_BEGIN) STOPPING SIMULATOR PACK...'

	@( docker stop $(SIMULATOR_CONTAINER_NAME) ) || true

	@echo '$(PATTERN_END) SIMULATOR PACK STOPPED!'	
# < DOCKER-SIMULATOR

# > SIMULATOR
run-simulator:
	@python3 -m flask run \
	--host=$(SIMULATOR_HOST) \
	--port=$(SIMULATOR_FLASK_PORT)
# < SIMULATOR

# > DB VOLUME
clean-db:
	@echo '$(PATTERN_BEGIN) CLEANING DB VOLUME...'

	@docker exec -it $(SIMULATOR_CONTAINER_NAME) bash -c "rm -rf $(DB_PATH)/energysim.db*"

	@echo '$(PATTERN_END) DB VOLUME CLEANED UP!'	

backup-db-export:
	@echo '$(PATTERN_BEGIN) EXPORTING DB VOLUME BACKUP...'

	@( docker run \
		--rm \
		--volume $(DB_VOLUME) \
		--volume $(shell pwd):/backup \
		bash -c "cd $(DB_PATH) && tar -cvf /backup/$(DB_VOLUME_BACKUP_FILENAME) *" \
		) \
		|| \
		true

	@echo '$(PATTERN_END) DB VOLUME BACKUP EXPORTED (to $(DB_VOLUME_BACKUP_FILENAME))!'

backup-db-import: 
	@echo '$(PATTERN_BEGIN) IMPORTING DB VOLUME BACKUP...'

	@( docker run \
		--rm \
		--volume $(DB_VOLUME) \
		--volume $(shell pwd):/backup \
		bash -c "cd $(DB_PATH) && tar -xvf /backup/$(DB_VOLUME_BACKUP_FILENAME)" \
		) \
		|| \
		true

	@echo '$(PATTERN_END) DB VOLUME BACKUP IMPORTED!'	
# < DB VOLUME

# > HELPERS
logs:
	@docker logs $(SIMULATOR_CONTAINER_NAME)

access-container:
	@docker exec -it $(SIMULATOR_CONTAINER_NAME) /bin/bash
# < HELPERS