"""Run the existing material tracer with bound model/library/source receipts."""
import argparse
import importlib.util
import json
from pathlib import Path
from placement_probe import sha


def trace(args):
    tool=Path(__file__).resolve().parents[2]/'docs/validation/siw-real-wedge-default/material_rays.py'
    def identity():
        return dict(compact_sha256=sha(args.compact),materials_sha256=sha(args.compact.parent/'materials.xml'),
            library_sha256={p.name:sha(p) for p in args.library},tracer_sha256=sha(tool),wrapper_sha256=sha(__file__))
    initial=identity()
    if args.output.exists() or args.output.with_suffix('.receipt.json').exists(): raise ValueError('Refusing ray evidence overwrite')
    spec=importlib.util.spec_from_file_location('nodd_existing_material_rays',tool);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    module.trace(args.compact,args.output,args.library)
    if identity()!=initial: raise ValueError('Material ray inputs changed during execution')
    receipt=dict(status='PASS',**initial,launch_identity_unchanged=True,rays_sha256=sha(args.output))
    args.output.with_suffix('.receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps(receipt,indent=2))


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--compact',type=Path,required=True)
    p.add_argument('--library',type=Path,action='append',required=True);p.add_argument('--output',type=Path,required=True);trace(p.parse_args())
