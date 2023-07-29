-include Makefile.local

all: 

include mk/pre_include.mk
include .devcontainer/rules.mk

help:
	@printf "Usage: make [target]                               \n";
	@printf "                                                   \n";
	@printf "Available targets:                                 \n";
	@printf "                                                   \n";
	@printf "\thelp                     Show this help message  \n";
	@printf "$(HELP_MSG)                                        \n";
	@printf "                                                   \n";

check: check-hadolint check-yamllint check-terraform check-ansible

check-hadolint:
	@hadolint .devcontainer/ubuntu.Dockerfile

check-ymllint:
	@yamllint -c .yamllint .

check-terraform:
	@terraform fmt -check -recursive -diff

check-ansible:
	@ansible-lint --offline --rules-dir infra/ansible role_path=./infra/ansible/roles/

clean:
	$(RM) -rf build
