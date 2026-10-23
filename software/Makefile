NODD_ROOT := $(abspath ..)
BUILD_DIR ?= $(NODD_ROOT)/build
JOBS ?= 6
ENV_RUN := $(NODD_ROOT)/software/env/run.sh
PYTHON ?= /Users/salzburg/Documents/work/installed/acts-nodd/pyvenv/bin/python
PLOT_PYTHON ?= $(NODD_ROOT)/software/build/unrooted-venv/bin/python
PROPAGATION_OUTPUT ?= $(BUILD_DIR)/tracker-propagation
.DEFAULT_GOAL := help
.PHONY: help doctor submodules submodule-status detector detector-test nodehammer idres check
help:
	@echo 'doctor             verify acts-mac-studio Spack runtime'
	@echo 'submodules         initialise pinned software sources (excludes Overleaf)'
	@echo 'submodule-status   show dependency revisions'
	@echo 'detector           build DD4hep factories and tracker compact'
	@echo 'detector-test      run DD4hep and exporter regression checks'
	@echo 'nodehammer         build the optional native viewer'
	@echo 'idres              build the optional IdRes tool'
	@echo 'check              validate infrastructure and project records'
	@echo 'tracker-propagation       build tracker, generate 3T map, propagate and plot'
	@echo 'tracker-propagation-plot  regenerate unrooted plots from saved count tables'
	@echo 'tracker-propagation-controls  paired numerical and independent-seed checks'
doctor:
	"$(ENV_RUN)" python3 "$(NODD_ROOT)/software/env/doctor.py"
submodules:
	GIT_LFS_SKIP_SMUDGE=1 git -C "$(NODD_ROOT)" submodule update --init -- software/submodules
submodule-status:
	git -C "$(NODD_ROOT)" submodule status -- software/submodules
detector:
	"$(ENV_RUN)" cmake -S "$(NODD_ROOT)" -B "$(BUILD_DIR)/dd4hep" -G Ninja -DCMAKE_BUILD_TYPE=RelWithDebInfo
	"$(ENV_RUN)" cmake --build "$(BUILD_DIR)/dd4hep" --parallel $(JOBS)
detector-test: detector
	"$(ENV_RUN)" ctest --test-dir "$(BUILD_DIR)/dd4hep" --output-on-failure -j $(JOBS)
nodehammer:
	"$(ENV_RUN)" python3 "$(NODD_ROOT)/tools/nodehammer/build.py" --source "$(NODD_ROOT)/software/submodules/nodehammer" --build "$(BUILD_DIR)/nodehammer" --jobs $(JOBS)
idres:
	"$(ENV_RUN)" python3 "$(NODD_ROOT)/software/env/build_idres.py" --source "$(NODD_ROOT)/software/submodules/IdRes" --build "$(BUILD_DIR)/idres" --jobs $(JOBS)
check:
	python3 -B "$(NODD_ROOT)/software/env/check_layout.py"
	cd "$(NODD_ROOT)" && python3 -B tools/session_logging/session_log.py validate
	cd "$(NODD_ROOT)" && python3 -B tools/project_records/validate.py
	cd "$(NODD_ROOT)" && python3 -B tools/token_usage/build.py validate

.PHONY: idres-run
idres-run: idres
	"$(ENV_RUN)" python3 -B "$(NODD_ROOT)/tools/tracker_layout/idres_adapter.py" --configuration "$(NODD_ROOT)/docs/design/DES-006-layouts.json" --checkout "$(NODD_ROOT)/software/submodules/IdRes" --binary "$(BUILD_DIR)/idres/bin/idres" --work "$(BUILD_DIR)/idres/study" --output "$(BUILD_DIR)/idres/results.json"

.PHONY: tracker-propagation tracker-propagation-plot tracker-propagation-controls
tracker-propagation: detector
	/bin/zsh "$(NODD_ROOT)/software/running/tracker_profiles.sh" --build-dir "$(BUILD_DIR)/dd4hep" --output "$(PROPAGATION_OUTPUT)" --plot-python "$(PLOT_PYTHON)" $(PROPAGATION_ARGS)
tracker-propagation-plot:
	"$(PLOT_PYTHON)" -I "$(NODD_ROOT)/tools/tracker_propagation/plot.py" --config "$(PROPAGATION_OUTPUT)/study.json" --directory "$(PROPAGATION_OUTPUT)" --output "$(PROPAGATION_OUTPUT)/plots"
tracker-propagation-controls:
	/bin/zsh "$(NODD_ROOT)/software/running/tracker_profiles.sh" --stage controls --build-dir "$(BUILD_DIR)/dd4hep" --output "$(PROPAGATION_OUTPUT)" --plot-python "$(PLOT_PYTHON)"
