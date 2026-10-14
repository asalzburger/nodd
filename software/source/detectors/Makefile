# Invoke the standalone detector project with the node-bound environment.
NODD_ROOT := $(abspath ../../..)
BUILD_DIR ?= $(NODD_ROOT)/build/dd4hep-standalone
JOBS ?= 6
ENV_RUN := $(NODD_ROOT)/software/env/run.sh
.PHONY: all test
all:
	"$(ENV_RUN)" cmake -S . -B "$(BUILD_DIR)" -G Ninja -DCMAKE_BUILD_TYPE=RelWithDebInfo
	"$(ENV_RUN)" cmake --build "$(BUILD_DIR)" --parallel $(JOBS)
test: all
	"$(ENV_RUN)" ctest --test-dir "$(BUILD_DIR)" --output-on-failure -j $(JOBS)
