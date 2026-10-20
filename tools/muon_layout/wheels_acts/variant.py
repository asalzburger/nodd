"""Build a reviewed domain-parameter variant while preserving the frozen engine.

The generated C++ differs only in configurable world/virtual entrance dimensions
and their metadata. Native stepping, root discovery, filters and counters stay
byte-identical to the pinned original implementation.
"""
import argparse
import hashlib
import json
from pathlib import Path

BASE_SHA256 = '1215ae28efebfa8e969d5197bbb9e4cc58adf3e6a1bcdff5b34053d30c073349'


def generate(source, output):
    raw = Path(source).read_bytes()
    if hashlib.sha256(raw).hexdigest() != BASE_SHA256:
        raise ValueError('Frozen native source changed; review variant before rebuilding')
    text = raw.decode()
    changes = []

    def replace(old, new, count=1):
        nonlocal text
        if text.count(old) != count:
            raise ValueError('Native variant anchor count changed: '+old)
        text = text.replace(old, new)
        changes.append(dict(old=old, new=new, occurrences=count))

    replace('constexpr double worldRadiusM = 9.1, worldHalfZM = 11.5;',
            'double worldRadiusM = 9.1, worldHalfZM = 11.5, entranceRadiusM = 4.35, entranceHalfZM = 6.5;')
    replace('struct Options {', 'struct Options {\n  double worldR=9.1, worldH=11.5, entranceR=4.35, entranceH=6.5;')
    replace('    else if(k=="--max-step-m")',
            '    else if(k=="--world-radius-m") o.worldR=std::stod(value());\n'
            '    else if(k=="--world-half-z-m") o.worldH=std::stod(value());\n'
            '    else if(k=="--entrance-radius-m") o.entranceR=std::stod(value());\n'
            '    else if(k=="--entrance-half-z-m") o.entranceH=std::stod(value());\n'
            '    else if(k=="--max-step-m")')
    replace('  return o;\n}',
            '  if(!(o.worldR>o.entranceR && o.worldH>o.entranceH && o.entranceR>0 && o.entranceH>0) ||\n'
            '     !std::isfinite(o.worldR+o.worldH+o.entranceR+o.entranceH)) throw std::runtime_error("invalid world/entrance dimensions");\n'
            '  return o;\n}')
    replace('4.35*U::m', 'entranceRadiusM*U::m', 2)
    replace('6.5*U::m', 'entranceHalfZM*U::m', 2)
    replace(r'\"entrance_radius_m\": 4.35', r'\"entrance_radius_m\": "<<entranceRadiusM<<"')
    replace(r'\"entrance_half_z_m\": 6.5', r'\"entrance_half_z_m\": "<<entranceHalfZM<<"')
    replace('auto started=std::chrono::steady_clock::now();auto o=arguments(argc,argv);',
            'auto started=std::chrono::steady_clock::now();auto o=arguments(argc,argv);\n'
            '    worldRadiusM=o.worldR;worldHalfZM=o.worldH;entranceRadiusM=o.entranceR;entranceHalfZM=o.entranceH;')
    output = Path(output)
    output.write_text(text)
    report = dict(base_source_sha256=BASE_SHA256,
                  variant_generator_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                  generated_source_sha256=hashlib.sha256(output.read_bytes()).hexdigest(),
                  scope='Only world/virtual entrance dimensions, CLI validation and corresponding metadata change.',
                  transformations=changes)
    output.with_suffix('.variant.json').write_text(json.dumps(report, indent=2)+'\n')
    return report


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    generate(args.source, args.output)
