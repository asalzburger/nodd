#!/usr/bin/env python3
"""Exact-hash, task-owned copies. Renaming and observation only; no guard."""
import hashlib
import json
from pathlib import Path
import re
import sys

source, build, output, own = map(Path, sys.argv[1:])
expected = {
    'Core/src/Seeding/GbtsTrackingFilter.cpp':'6fa5dc68793b8f54fb65d3d07badc33657e3c182e6c70d1ec65ab39793db9afa',
    'Core/include/Acts/Seeding/GbtsTrackingFilter.hpp':'c46537bd8108032e0cce550c3d9bc3fe7c1b161473aec361c488d2a92b2996a5',
    'Core/src/Seeding/GraphBasedTrackSeeder.cpp':'d3d0b2f4c7912228d7cf71dd8d4a00f52a2acd16eb98b991bd49f4144d63d4e1',
    'Core/include/Acts/Seeding/GraphBasedTrackSeeder.hpp':'4ad092a79a8f6c7190e942580f6c6cba54b7aa7698b3803576e233229d1f4948',
    'Core/include/Acts/Seeding/detail/GbtsFilterTypes.hpp':'aa6f727d24cd3a6ee0250738955bf33a4dd900af02abc44c142121288a3e358b',
    'Core/src/Seeding/GbtsGeometry.cpp':'746375308afeb950dc3fd4147066f896beb6016b17a0a6aa571e44023cf1ec5a',
    'Core/src/Seeding/GbtsNodeStorage.cpp':'85fb06df24bec639cf5cdd533e2362450af55d5e505db2604d2934cae7e0c7e5',
    'Core/include/Acts/Seeding/GbtsGeometry.hpp':'19ac241c834d357d2f4fa3c8226c6b38ee5c35e501cbd6e38be6f7b23b3a91bd',
    'Core/include/Acts/Seeding/GbtsNodeStorage.hpp':'833bc8279989edac1ee7b2d330e687d9e832df03e2c703fe1e4e43b9464a9fdd',
    'Core/include/Acts/Seeding/detail/GbtsLayer.hpp':'4110604ea949345c2e25cb44acc42ca4d3e0aa631433e7b4b913882d50351241',
}
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
for name, digest in expected.items():
    if sha(source/name)!=digest: raise RuntimeError('Upstream source changed: '+name)
ninja=(build/'build.ninja').read_text()
blocks={}
for name in ('GbtsTrackingFilter','GraphBasedTrackSeeder','GbtsGeometry','GbtsNodeStorage'):
    block=ninja.split('build Core/CMakeFiles/ActsCore.dir/src/Seeding/'+name+'.cpp.o:',1)[1].split('\n\n',1)[0]
    flags=re.search(r'  FLAGS = (.+)',block)[1]
    defines=re.search(r'  DEFINES = (.+)',block)[1]
    blocks[name]=dict(flags=flags,defines=defines,block_sha256=hashlib.sha256(block.encode()).hexdigest())
assert blocks['GbtsTrackingFilter']['flags']==blocks['GraphBasedTrackSeeder']['flags']
assert blocks['GbtsTrackingFilter']['defines']==blocks['GraphBasedTrackSeeder']['defines']
assert '-O2 -g -DNDEBUG -std=gnu++20 -fPIC' in flags
assert not any(x in flags for x in ('fast-math','flto','Ofast'))
# CMake parses the exact native macros using UNIX_COMMAND, preserving ABI quotes.
(output/'native.cmake').write_text('set(NODD_NATIVE_FLAGS [=['+flags+']=])\nset(NODD_NATIVE_DEFINES [=['+defines+']=])\n')
def once(text,before,after):
    if text.count(before)!=1: raise RuntimeError('Anchor count changed: '+before)
    return text.replace(before,after)
generated={}
for variant in ('Renamed','Observed'):
    for name in expected:
        text=(source/name).read_text()
        if variant=='Observed' and name.endswith('/GbtsTrackingFilter.cpp'):
            text=once(text,'#include <algorithm>','#include "DivisionAudit.hpp"\n#include <algorithm>')
            text=once(text,'  // add ms.','  nodd::gbts::nextUpdate();\n  // add ms.')
            text=once(text,'  const float lenCorr =', '''  if(layerType1 != GbtsLayerType::Barrel)
    nodd::gbts::observe("lenCorr",tau2,ts,n1,n2);
  nodd::gbts::observe("minPtFrac",m_cfg.maxCurvature,ts,n1,n2);
  const float lenCorr =''')
            for axis,cov,sigma in [('x','Cx','sigmaX * sigmaX'),('y','Cy','sigma_rz')]:
                anchor=f'  const float D{axis} = 1.0f / ({cov}[0][0] + {sigma});'
                observation=f'''  if(nodd::gbts::observe("D{axis}",{cov}[0][0] + {sigma},ts,n1,n2)) {{
    auto& audit=nodd::gbts::records().back();
    audit["predicted_x_bits"]=nodd::gbts::bits(X);audit["predicted_y_bits"]=nodd::gbts::bits(Y);
    audit["predicted_cov_x_bits"]=nodd::gbts::bits(Cx);audit["predicted_cov_y_bits"]=nodd::gbts::bits(Cy);
    audit["sigma_bits"]={{nodd::gbts::bits(sigmaX),nodd::gbts::bits(sigmaY),nodd::gbts::bits(sigma_rz)}};
    audit["residual_bits"]={{nodd::gbts::bits(resid_x),nodd::gbts::bits(resid_y)}};
  }}
'''
                text=once(text,anchor,observation+anchor)
        # Replace include paths before type tokens, including the friend and
        # out-of-line initialize symbol; no shared declaration is shadowed.
        text=text.replace('Acts/Seeding/detail/GbtsFilterTypes.hpp',f'nodd/gbts/Nodd{variant}GbtsFilterTypes.hpp')
        text=text.replace('Acts/Seeding/detail/GbtsLayer.hpp',f'nodd/gbts/Nodd{variant}GbtsLayer.hpp')
        for token in ('GraphBasedTrackSeeder','GbtsTrackingFilter','GbtsNodeStorage','GbtsGeometry'):
            text=text.replace('Acts/Seeding/'+token+'.hpp',f'nodd/gbts/Nodd{variant}'+token+'.hpp')
        for token in ('GraphBasedTrackSeeder','GbtsTrackingFilter','GbtsEdgeState','GbtsFilterState','kGbtsMaxEdgeStates','GbtsNodeStorage','GbtsGeometry','GbtsLayer','GbtsZ0Range'):
            text=re.sub(r'\b'+token+r'\b','Nodd'+variant+token,text)
        filename='Nodd'+variant+Path(name).name
        path=output/'nodd/gbts'/filename if name.endswith('.hpp') else output/filename
        path.parent.mkdir(parents=True,exist_ok=True);path.write_text(text)
        generated[str(path.relative_to(output))]=sha(path)
local={p.name:sha(p) for p in sorted(own.iterdir()) if p.is_file()}
provenance=dict(acts_revision='355ea68493b326956756c9386d2fd9eaf9328568',upstream_sha256=expected,
    generated_sha256=generated,local_source_sha256=local,native_objects=blocks,
    compiler_cache_sha256=sha(build/'CMakeCache.txt'),native_build_ninja_sha256=sha(build/'build.ninja'))
payload=json.dumps(provenance,sort_keys=True,separators=(',',':'))
(output/'GbtsProvenance.hpp').write_text('inline const char* noddGbtsProvenance(){ return R"nodd('+payload+')nodd"; }\n')
(output/'provenance.json').write_text(json.dumps(provenance,indent=2)+'\n')
