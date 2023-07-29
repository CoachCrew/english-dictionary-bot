define print_cmd 
	@printf '\033[1;34m'
	@printf '$(1)'
	@printf '\033[0m'
endef

define prompt_approval
	@printf '\033[1;31m'
	@read -p "Are you sure you want to proceed? [Y/n]: " -r response
	@printf '\033[0m'
endef
