# All software recipes live with their source tree.
.DEFAULT_GOAL := help
.PHONY: help doctor submodules submodule-status detector detector-test nodehammer idres check
help doctor submodules submodule-status detector detector-test nodehammer idres check:
	+$(MAKE) -C software $@
