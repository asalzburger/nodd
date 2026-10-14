"""Build IdRes in a disposable copy, keeping its submodule pristine."""
import argparse
from pathlib import Path
import shutil
import subprocess

p = argparse.ArgumentParser(description=__doc__)
p.add_argument("--source", type=Path, required=True)
p.add_argument("--build", type=Path, required=True)
p.add_argument("--jobs", type=int, default=4)
a = p.parse_args()
if not (a.source / "src/Makefile").is_file():
    p.error("Initialise the IdRes submodule first")
if a.jobs < 1:
    p.error("jobs must be positive")
# Copy only upstream build inputs; objects and executables never enter the submodule.
a.build.mkdir(parents=True, exist_ok=True)
shutil.copytree(a.source / "src", a.build / "src", dirs_exist_ok=True,
                ignore=shutil.ignore_patterns("*.o", "idres"))
(a.build / "bin").mkdir(exist_ok=True)
flags = subprocess.check_output(["gsl-config", "--cflags"], text=True).strip()
libs = subprocess.check_output(["gsl-config", "--libs"], text=True).strip()
subprocess.run(["make", "-C", str(a.build / "src"), f"-j{a.jobs}",
                f"CPPFLAGS={flags}", f"LDFLAGS={libs}"], check=True)
