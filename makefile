PATTERN_BEGIN=>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
PATTERN_END=<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<

BUILDPACK_BUILDER=heroku/buildpacks:18
BUILDPACK_NAME=tukxi-simulator

PORT=7777

main: prep build stop exec

prep:
	@echo '$(PATTERN_BEGIN) PREPARING...'
	@pipreqs ./ --force
	@pack set-default-builder $(BUILDPACK_BUILDER)
	@echo '$(PATTERN_END) PREPARED!'

build:
	@echo '$(PATTERN_BEGIN) BUILDING...'
	@pack build $(BUILDPACK_NAME)
	@echo '$(PATTERN_END) BUILD COMPLETE!'

stop:
	@echo '$(PATTERN_BEGIN) STOPPING...'
	@docker stop $(BUILDPACK_NAME) && docker rm $(BUILDPACK_NAME)
	@echo '$(PATTERN_END) STOPPED!'

exec:
	@echo '$(PATTERN_BEGIN) RUNNING...'
	@docker run -d -ePORT=$(PORT) -p$(PORT):$(PORT) --name $(BUILDPACK_NAME) $(BUILDPACK_NAME)
	@echo '$(PATTERN_END) RUN COMPLETE!'

test:
	@FLASK_APP=main python3 -m flask run --host=0.0.0.0 --port=$(PORT)