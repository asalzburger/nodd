# All software recipes live with their source tree.
.DEFAULT_GOAL := help
.PHONY: help doctor submodules submodule-status detector detector-test nodehammer idres idres-run check tracker-propagation tracker-propagation-plot tracker-propagation-controls
help doctor submodules submodule-status detector detector-test nodehammer idres idres-run check tracker-propagation tracker-propagation-plot tracker-propagation-controls:
	+$(MAKE) -C software $@

.PHONY: key4hep-submodules key4hep key4hep-test
key4hep-submodules key4hep key4hep-test:
	+$(MAKE) -C software $@
