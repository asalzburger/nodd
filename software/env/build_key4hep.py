#!/usr/bin/env python3
"""Build the pinned original RecCaloDigi runtime against the active ACTS Spack view.

Run through software/env/run.sh. No package downloads or shared Spack mutations.
All generated files, logs and installs stay under software/build/key4hep.
"""
import argparse
import json
import os
from pathlib import Path
import shlex
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
SOURCES = ROOT / 'software/submodules'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--jobs', type=int, default=6)
    parser.add_argument('--stage', choices=('all', 'boost', 'headers', 'Gaudi', 'k4FWCore', 'reference'), default='all')
    args = parser.parse_args()
    if args.jobs < 1:
        parser.error('--jobs must be positive')
    expected_env = '/Users/salzburg/Documents/work/externals/ci-dependencies'
    if os.environ.get('SPACK_ENV') != expected_env:
        parser.error('activate the existing ACTS Spack environment with software/env/run.sh')
    build = ROOT / 'software/build/key4hep'
    prefix = build / 'install'
    build.mkdir(parents=True, exist_ok=True)
    env = os.environ.copy()
    env['CMAKE_PREFIX_PATH'] = str(prefix) + os.pathsep + env.get('CMAKE_PREFIX_PATH', '')
    env['PATH'] = str(prefix / 'bin') + os.pathsep + env['PATH']
    env['PYTHONPATH'] = str(prefix / 'python') + os.pathsep + env.get('PYTHONPATH', '')
    env['GAUDI_PLUGIN_PATH'] = str(prefix / 'lib')
    env['LD_LIBRARY_PATH'] = str(prefix / 'lib') + os.pathsep + env.get('LD_LIBRARY_PATH', '')
    env['DYLD_LIBRARY_PATH'] = str(prefix / 'lib') + os.pathsep + env.get('DYLD_LIBRARY_PATH', '')
    pins = json.loads((ROOT / 'software/env/key4hep-pins.json').read_text())
    for name, revision in pins.items():
        actual = subprocess.check_output(['git', '-C', str(SOURCES / name), 'rev-parse', 'HEAD'], text=True).strip()
        if actual != revision:
            parser.error(f'{name}: require {revision}, got {actual}')
        if subprocess.check_output(['git', '-C', str(SOURCES / name), 'diff', 'HEAD', '--'], text=True).strip():
            parser.error(f'{name}: modified tracked source; use the pinned clean source')

    def run(label, command):
        print(shlex.join(map(str, command)), flush=True)
        with (build / (label + '.log')).open('w') as log:
            completed = subprocess.run(list(map(str, command)), env=env, stdout=log, stderr=subprocess.STDOUT)
        if completed.returncode:
            print((build / (label + '.log')).read_text()[-12000:], file=sys.stderr)
            raise SystemExit(completed.returncode)

    common = ['-G', 'Ninja', '-DCMAKE_BUILD_TYPE=Release', f'-DCMAKE_INSTALL_PREFIX={prefix}',
              '-DCMAKE_INSTALL_LIBDIR=lib', '-DGAUDI_INSTALL_PYTHONDIR=python', '-DGAUDI_INSTALL_PLUGINDIR=lib',
              '-DCMAKE_FIND_FRAMEWORK=LAST', '-DCMAKE_INSTALL_RPATH_USE_LINK_PATH=ON',
              f'-DCMAKE_INSTALL_RPATH={prefix / "lib"}', '-DBUILD_TESTING=OFF',
              f'-DPython_EXECUTABLE={sys.executable}']
    stages = [
        ('boost', SOURCES / 'boost', ['-DBUILD_SHARED_LIBS=ON', '-DBOOST_ENABLE_CMAKE=ON', '-DBOOST_ENABLE_PYTHON=ON',
            '-DBOOST_INCLUDE_LIBRARIES=filesystem;regex;fiber;thread;python;test;program_options;log;graph']),
        ('range-v3', SOURCES / 'range-v3', ['-DRANGE_V3_TESTS=OFF', '-DRANGE_V3_EXAMPLES=OFF', '-DRANGE_V3_PERF=OFF']),
        ('GSL', SOURCES / 'GSL', ['-DGSL_TEST=OFF']),
        ('Gaudi', SOURCES / 'Gaudi', ['-DGAUDI_BUILD_EXAMPLES=OFF', '-DGAUDI_ENABLE_GAUDIPARTPROP=OFF',
            '-DGAUDI_USE_AIDA=OFF', '-DGAUDI_USE_HEPPDT=OFF', '-DGAUDI_USE_DOXYGEN=OFF',
            '-DGAUDI_USE_XERCESC=OFF', '-DGAUDI_USE_ZSTD=OFF', '-UUUID_INCLUDE_DIR',
            f'-DBoost_DIR={prefix / "lib/cmake/Boost-1.90.0"}']),
        ('k4FWCore', SOURCES / 'k4FWCore', []),
        ('reference', ROOT / 'software/source/Key4hepReference', []),
    ]
    for name, source, options in stages:
        if args.stage != 'all' and name != args.stage and not (args.stage == 'headers' and name in ('range-v3', 'GSL')):
            continue
        target = build / name
        run(name + '-configure', ['cmake', '-S', source, '-B', target, *common, *options])
        run(name + '-build', ['cmake', '--build', target, '--parallel', args.jobs])
        run(name + '-install', ['cmake', '--install', target])
    (build / 'source-pins.json').write_text(json.dumps(pins, indent=2) + '\n')
    print(f'Local installation: {prefix}')


if __name__ == '__main__':
    main()
