# All software recipes live with their source tree.
.DEFAULT_GOAL := help
.PHONY: help doctor submodules submodule-status detector detector-test nodehammer idres idres-run check
help doctor submodules submodule-status detector detector-test nodehammer idres idres-run check:
	+$(MAKE) -C software $@
