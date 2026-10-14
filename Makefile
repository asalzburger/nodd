# All software recipes live with their source tree.
.DEFAULT_GOAL := help
.PHONY: all test help doctor submodules submodule-status detector detector-test nodehammer idres idres-run check software-python software-configure software software-test geometry material analysis install
all test help doctor submodules submodule-status detector detector-test nodehammer idres idres-run check software-python software-configure software software-test geometry material analysis install:
	+$(MAKE) -C software $@
