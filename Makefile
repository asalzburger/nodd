# All software recipes live with their source tree.
.DEFAULT_GOAL := help
.PHONY: all test help doctor submodules submodule-status detector detector-test nodehammer idres check software-python software-configure software software-test geometry material analysis install calorimeter calorimeter-test calorimeter-run calorimeter-analysis
all test help doctor submodules submodule-status detector detector-test nodehammer idres check software-python software-configure software software-test geometry material analysis install calorimeter calorimeter-test calorimeter-run calorimeter-analysis:
	+$(MAKE) -C software $@
