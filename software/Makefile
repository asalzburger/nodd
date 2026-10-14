NODD_ROOT := $(abspath ..)
BUILD_DIR ?= $(NODD_ROOT)/build
JOBS ?= 6
ENV_RUN := $(NODD_ROOT)/software/env/run.sh
PYTHON ?= $(BUILD_DIR)/pyvenv/bin/python
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
	@echo 'software           build ACTS with local nODD extensions'
	@echo 'software-test      run Gen3 and Geant4 adapter regression tests'
	@echo 'geometry/material  execute Python steering jobs'
	@echo 'analysis           compare saved Gen3 report with native inventory'
	@echo 'install            install into the local build prefix'
	@echo 'calorimeter-test   run migrated reconstruction/EDM4hep controls'
	@echo 'calorimeter-run    run a Python-steered synthetic calorimeter job'
	@echo 'check              validate infrastructure and project records'
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

# ACTS remains CMake's top-level project. The external hook appends nODD targets.
ACTS_BUILD_DIR ?= $(BUILD_DIR)/acts
CMAKE_ARGS ?=
ACTS_OPTIONS := -DCMAKE_BUILD_TYPE=RelWithDebInfo -DCMAKE_CXX_STANDARD=20 \
  -DCMAKE_INSTALL_PREFIX=$(BUILD_DIR)/installed \
  -DPython_EXECUTABLE=$(PYTHON) -DPython3_EXECUTABLE=$(PYTHON) \
  -DACTS_USE_SYSTEM_LIBS=ON -DACTS_GENERATE_PYTHON_STUBS=OFF \
  -DACTS_BUILD_ODD=OFF -DACTS_BUILD_EXAMPLES=ON \
  -DACTS_BUILD_EXAMPLES_DD4HEP=ON -DACTS_BUILD_EXAMPLES_ROOT=ON \
  -DACTS_BUILD_EXAMPLES_GEANT4=ON -DACTS_BUILD_EXAMPLES_PODIO=ON \
  -DACTS_BUILD_EXAMPLES_EDM4HEP=ON -DACTS_BUILD_EXAMPLES_FASTJET=ON \
  -DACTS_BUILD_PLUGIN_DD4HEP=ON -DACTS_BUILD_PLUGIN_GEANT4=ON \
  -DACTS_BUILD_PLUGIN_ROOT=ON -DACTS_BUILD_PLUGIN_JSON=ON \
  -DACTS_BUILD_PLUGIN_EDM4HEP=ON -DACTS_BUILD_PYTHON_BINDINGS=ON \
  -DACTS_BUILD_UNITTESTS=ON -DACTS_BUILD_CORE_UNITTESTS=OFF \
  -DACTS_BUILD_EXAMPLES_UNITTESTS=OFF
ACTS_RUN := "$(ENV_RUN)" "$(NODD_ROOT)/software/env/acts-run.sh" "$(ACTS_BUILD_DIR)"
.PHONY: software-python software-configure software software-test geometry material analysis install
software-python:
	UV_CACHE_DIR="$(BUILD_DIR)/uv-cache" "$(ENV_RUN)" python3 "$(NODD_ROOT)/software/env/bootstrap_python.py" --venv "$(BUILD_DIR)/pyvenv"
software-configure: software-python
	"$(ENV_RUN)" cmake -S "$(NODD_ROOT)/software/submodules/acts" -B "$(ACTS_BUILD_DIR)" -G Ninja $(ACTS_OPTIONS) -DCMAKE_PROJECT_Acts_INCLUDE="$(NODD_ROOT)/software/source/ActsExamples/cmake/Inject.cmake" $(CMAKE_ARGS)
software: software-python
	@test -f "$(ACTS_BUILD_DIR)/build.ninja" || $(MAKE) software-configure
	"$(ENV_RUN)" cmake --build "$(ACTS_BUILD_DIR)" --parallel $(JOBS) --target nodd-software
software-test: software detector
	$(ACTS_RUN) env NODD_PATH="$(NODD_ROOT)" NODD_BUILD_DIR="$(BUILD_DIR)/dd4hep" "$(PYTHON)" -m pytest -q "$(NODD_ROOT)/software/source/ActsExamples/Nodd/Tests"
geometry: software detector
	$(ACTS_RUN) "$(PYTHON)" "$(NODD_ROOT)/software/running/nodd_geometry_validation.py" --nodd-dir "$(NODD_ROOT)" --build-dir "$(BUILD_DIR)/dd4hep" --output "$(BUILD_DIR)/jobs/geometry" --tracks 128
material: software detector
	$(ACTS_RUN) "$(PYTHON)" "$(NODD_ROOT)/software/running/nodd_material_recording.py" --nodd-dir "$(NODD_ROOT)" --build-dir "$(BUILD_DIR)/dd4hep" --events 1 --tracks 8 --output "$(BUILD_DIR)/jobs/material"
analysis:
	$(ACTS_RUN) "$(PYTHON)" "$(NODD_ROOT)/software/analysis/check_geometry.py" --report "$(BUILD_DIR)/jobs/geometry/surfaces.json" --expected "$(BUILD_DIR)/dd4hep/detector/tracker/expected.json" --output "$(BUILD_DIR)/jobs/geometry/comparison.json"
install: software detector
	"$(ENV_RUN)" cmake --build "$(ACTS_BUILD_DIR)" --parallel $(JOBS) --target install
	"$(ENV_RUN)" cmake --install "$(BUILD_DIR)/dd4hep" --prefix "$(BUILD_DIR)/installed"

.PHONY: all test
all: detector software
test: detector-test software-test calorimeter-test

.PHONY: calorimeter calorimeter-test calorimeter-run calorimeter-analysis
calorimeter: software
calorimeter-test: calorimeter
	"$(ENV_RUN)" ctest --test-dir "$(ACTS_BUILD_DIR)" -R '^Calorimeter' --output-on-failure -j $(JOBS)
CALORIMETER_MODE ?= edm4hep-jets
calorimeter-run: calorimeter
	$(ACTS_RUN) "$(PYTHON)" "$(NODD_ROOT)/software/running/calorimeter.py" --build-dir "$(ACTS_BUILD_DIR)" --mode $(CALORIMETER_MODE) --output "$(BUILD_DIR)/jobs/calorimeter/$(CALORIMETER_MODE)"
calorimeter-analysis:
	$(ACTS_RUN) "$(PYTHON)" "$(NODD_ROOT)/software/analysis/inspect_calorimeter.py" --input "$(BUILD_DIR)/jobs/calorimeter/$(CALORIMETER_MODE)" --output "$(BUILD_DIR)/jobs/calorimeter/$(CALORIMETER_MODE)/inspection.json"
