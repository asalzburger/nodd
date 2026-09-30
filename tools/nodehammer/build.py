#!/usr/bin/env python3
"""Build the pinned optional viewer; run after activating DD4hep/ROOT."""

import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess

ROOT = Path(__file__).resolve().parents[2]


def run(*args, **kwargs):
    subprocess.run([str(arg) for arg in args], check=True, **kwargs)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=ROOT / "reference/cache/nodehammer")
    parser.add_argument("--build", type=Path, default=ROOT / "build/nodehammer")
    parser.add_argument("--jobs", type=int, default=4)
    args = parser.parse_args()
    pin = json.loads(Path(__file__).with_name("upstream.json").read_text())
    for executable in ("root-config", "cmake", "ninja", "uv", "python3"):
        if not shutil.which(executable):
            parser.error(f"{executable} missing; activate the documented DD4hep environment first")
    source, build = args.source.resolve(), args.build.resolve()
    build.mkdir(parents=True, exist_ok=True)
    if not source.exists():
        run("git", "clone", pin["repository"], source)
        run("git", "-C", source, "checkout", "--detach", pin["revision"])
    head = subprocess.check_output(["git", "-C", str(source), "rev-parse", "HEAD"], text=True).strip()
    dirty = subprocess.check_output(["git", "-C", str(source), "status", "--porcelain", "--untracked-files=no"], text=True)
    if head != pin["revision"] or dirty:
        parser.error("source must be clean at upstream.json revision; existing checkout left untouched")
    os.environ["CONAN_HOME"] = str(build / "conan")
    os.environ["UV_CACHE_DIR"] = str(build / "uv-cache")
    env = build / "tools-spack-env"
    if not env.exists():
        run("uv", "venv", "--python", shutil.which("python3"), env)
    run("uv", "pip", "install", "--python", env / "bin/python", f"conan=={pin['conan_version']}")
    conan = env / "bin/conan"
    if not (build / "conan/profiles/nodd").exists():
        run(conan, "profile", "detect", "--name", "nodd")
    for recipe, version in pin["recipes"].items():
        run(conan, "export", source / "recipes" / recipe, f"--version={version}")
    lock = build / "conan.lock"
    reference_lock = lock if lock.exists() else Path(__file__).with_name("conan.lock")
    run(conan, "install", source, "-of", build / "deps", "-pr:a", "nodd",
        "-s", "build_type=RelWithDebInfo", "-s:a", "compiler.cppstd=23",
        "--build=missing", "-c", "tools.cmake.cmaketoolchain:generator=Ninja",
        "-o", "viewer=True", f"--lockfile-out={lock}",
        f"--lockfile={reference_lock}")
    run("cmake", "-S", source, "-B", build / "native", "-G", "Ninja",
        f"-DCMAKE_TOOLCHAIN_FILE={build}/deps/build/RelWithDebInfo/generators/conan_toolchain.cmake",
        "-DCMAKE_BUILD_TYPE=RelWithDebInfo", "-DNODEHAMMER_WITH_TGEO=ON",
        "-DNODEHAMMER_WITH_DD4HEP=ON", "-DNODEHAMMER_WITH_VIEWER=ON",
        "-DNODEHAMMER_BUILD_TESTS=ON")
    run("cmake", "--build", build / "native", "--parallel", args.jobs)
    run("ctest", "--test-dir", build / "native", "--output-on-failure", "-j", args.jobs)
    executable = build / "native/nodehammer"
    manifest = {"upstream_revision": head,
                "nodehammer_sha256": hashlib.sha256(executable.read_bytes()).hexdigest(),
                "conan_lock_sha256": hashlib.sha256(lock.read_bytes()).hexdigest(),
                "conan_profile": (build / "conan/profiles/nodd").read_text(),
                "conan_settings_overrides": {"build_type": "RelWithDebInfo", "compiler.cppstd": "23"},
                "capabilities": ["DD4hep", "TGeo", "native viewer"],
                "root_version": subprocess.check_output(["root-config", "--version"], text=True).strip(),
                "cmake_version": subprocess.check_output(["cmake", "--version"], text=True).splitlines()[0],
                "conan_version": pin["conan_version"]}
    (build / "build-manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")


if __name__ == "__main__":
    main()
