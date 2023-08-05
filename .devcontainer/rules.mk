# ============================================================================= #
# Version  v1.1.0                                                               #
# Date     2023.06.08                                                           #
# CoachCrew.tech                                                                #
# admin@CoachCrew.tech                                                          #
# ============================================================================= #

.PHONY: help build-image run-develop run-test

CONTAINER_DIR      ?= .devcontainer
WORK_DIR           ?= $(shell pwd)/..
USERNAME           ?= testuser
USER_UID           ?= 1000
USER_GID           ?= 1000

IMAGE_NAME         ?= langenscheidt
CONTAINER_NAME     ?= $(IMAGE_NAME)-$(USERNAME)-$(shell date +"%Y-%m-%d.%H-%M")
DOCKER_FILE        ?= $(CONTAINER_DIR)/ubuntu.Dockerfile
DOCKER_ENTRYPOINT  ?= $(CONTAINER_DIR)/develop-entrypoint.sh
SHARED_DIRS        ?= $(WORK_DIR)
RULES_MK           ?= $(CONTAINER_DIR)/rules.mk

BUILD_IMAGE        ?= $(CONTAINER_DIR)/build-image
DIRECTORIES        ?= $(CONTAINER_DIR)/directories

HELP_MSG          += \trun-develop              Run\
	a container from the ${IMAGE_NAME} image\n
HELP_MSG          += \tbuild-image              Build\
	the docker images ${IMAGE_NAME} with the required dependencies\n

directories: $(DIRECTORIES)

$(DIRECTORIES):
	$(foreach dir, $(SHARED_DIRS), mkdir -p $(dir);)
	@touch $@

build-image: $(BUILD_IMAGE) $(DOCKER_ENTRYPOINT) $(RULES_MK)

$(BUILD_IMAGE): $(DOCKER_FILE) $(DOCKER_SCRIPTS) $(DOCKER_ENTRYPOINT)
	$(call print_cmd,\ndocker build -t $(IMAGE_NAME)                        \n)
	$(call print_cmd,   --build-arg DOCKER_ENTRYPOINT=$(DOCKER_ENTRYPOINT)  \n)
	$(call print_cmd,   --file $(DOCKER_FILE) .                           \n\n)

	$(call prompt_approval)

	@docker build -t $(IMAGE_NAME)                             \
		--build-arg DOCKER_ENTRYPOINT=$(DOCKER_ENTRYPOINT) \
		--file $(DOCKER_FILE) .
	@touch $@

run-develop: build-image directories
	$(call print_cmd, docker run -it --rm                               \n)
	$(call print_cmd,    --name $(CONTAINER_NAME)                       \n)
	$(call print_cmd,    --network host                                 \n)
	$(call print_cmd,    --env USERNAME=$(USERNAME)                     \n)
	$(call print_cmd,    --env USER_UID=$(USER_UID)                     \n)
	$(call print_cmd,    --env USER_GID=$(USER_GID)                     \n)
	$(call print_cmd,    --env PYTHON_REQ=$(PYTHON_REQ)                 \n)
	$(call print_cmd,    --env WORK_DIR=$(WORK_DIR)                     \n)
	$(call print_cmd,  $(foreach dir, $(SHARED_DIRS),  --volume $(dir):$(dir) \n))
	$(call print_cmd, $(IMAGE_NAME)\n\n)

	$(call prompt_approval)	

	@docker run -it --rm                                     \
		--name $(CONTAINER_NAME)                         \
		--network host                                   \
		--env AWS_ACCESS_KEY_ID=$(AWS_ACCESS_KEY_ID)     \
		--env AWS_SECRET_ACCESS_KEY=$(AWS_ACCESS_KEY_ID) \
		--env USERNAME=$(USERNAME)                       \
		--env USER_UID=$(USER_UID)                       \
		--env USER_GID=$(USER_GID)                       \
		--env PYTHON_REQ=$(PYTHON_REQ)                   \
		--env WORK_DIR=$(WORK_DIR)                       \
		$(foreach dir, $(SHARED_DIRS), -v $(dir):$(dir)) \
		$(IMAGE_NAME)

clean-image:
	@docker rmi --force $(IMAGE_NAME)
	@rm -rf $(BUILD_IMAGE)
	@rm -rf $(DIRECTORIES)
