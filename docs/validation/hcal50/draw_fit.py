"""Draw the DES045 envelope proposal and unchanged physical tile footprint."""
import hashlib
import importlib.util
import json
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

ROOT = Path(__file__).resolve().parents[3]


def main():
    config_path = ROOT / 'tools/hcal_response/config.json'
    c = json.loads(config_path.read_text()); b = c['barrel']; e = c['endcap']
    selected = json.loads((ROOT / 'detector/config/ecal-baseline.json').read_text())
    if selected['variant'] != 'LAR-RESTORED-SAMPLING-2026-11-18':
        raise ValueError('Envelope context requires the selected restored ECAL')
    layout_path = ROOT / 'docs/layouts/LAYOUT-002-restored.json'
    layout = json.loads(layout_path.read_text())
    for path, key in ((ROOT / 'detector/config/ecal-baseline.json', 'selection_sha256'),
                      (ROOT / selected['variant_spec'], 'variant_spec_sha256')):
        if hashlib.sha256(path.read_bytes()).hexdigest() != layout['source']['selection'][key]:
            raise ValueError('Named ECAL envelope provenance differs from the current selection')
    eb, ee = layout['barrel'], layout['endcaps']
    spec = importlib.util.spec_from_file_location('hcal_unit_drawing', ROOT / 'tools/hcal_readout/readout.py')
    unit_module = importlib.util.module_from_spec(spec); spec.loader.exec_module(unit_module)
    unit, _ = unit_module.build(absorber=False)
    out = Path(__file__).resolve().parent / 'figures'; out.mkdir(exist_ok=True)
    plt.rcParams.update({'font.size': 10, 'axes.spines.top': False, 'axes.spines.right': False, 'savefig.dpi': 180})
    fig, axes = plt.subplots(1, 2, figsize=(13, 5.7), layout='constrained', gridspec_kw={'width_ratios': [1.35, 1]})
    axis = axes[0]
    def rect(x, y, w, h, color, label=None, alpha=1, edge=None):
        axis.add_patch(Rectangle((x/1000, y/1000), w/1000, h/1000,
                                 facecolor=color, edgecolor=edge or color, alpha=alpha, label=label))
    rect(-eb['warm_half_z_mm'], eb['inner_radius_mm'], 2*eb['warm_half_z_mm'],
         eb['outer_radius_mm']-eb['inner_radius_mm'], '#cccc00', 'Selected LAr ECAL context')
    for sign in (-1, 1):
        rect(ee['warm_front_z_mm'] if sign > 0 else -ee['warm_back_z_mm'], ee['warm_inner_radius_mm'],
             ee['warm_back_z_mm']-ee['warm_front_z_mm'], ee['warm_outer_radius_mm']-ee['warm_inner_radius_mm'], '#cccc00')
    rect(-b['half_z_mm'], b['front_apothem_mm'], 2*b['half_z_mm'], b['outer_apothem_mm']-b['front_apothem_mm'], '#cc6600', 'HCAL · 60 sampling layers')
    for sign in (-1, 1):
        rect(e['front_abs_z_mm'] if sign > 0 else -e['back_abs_z_mm'], e['inner_apothem_mm'],
             e['back_abs_z_mm']-e['front_abs_z_mm'], e['outer_apothem_mm']-e['inner_apothem_mm'], '#cc6600')
        start = b['half_z_mm'] if sign > 0 else -e['front_abs_z_mm']
        rect(start, ee['warm_outer_radius_mm'], e['front_abs_z_mm']-b['half_z_mm'],
             e['outer_apothem_mm']-ee['warm_outer_radius_mm'], '#f5dfca',
             'Rear service reservation' if sign > 0 else None, alpha=.8)
    axis.axhline(c['radial_handoff_mm']/1000, color='#777777', ls='--', lw=1, label='Proposed outer handoff reservation')
    axis.set(xlabel='z [m]', ylabel='Face-normal radius / apothem [m]', xlim=(-9.8, 9.8), ylim=(0, 6.3), title='Envelope fit around the restored ECAL')
    axis.text(0, 4.4, '60 × (30 mm steel + 12 mm carrier + 1 mm gap)\n+ 10 mm rear cover = 2590 mm', ha='center', color='white', fontsize=9)
    axis.text(0, .35, 'Standalone run removes the ECAL shown here as context', ha='center', fontsize=8)
    axis.legend(loc='upper center', fontsize=7.7, ncol=2)
    axis.grid(alpha=.13)
    axis = axes[1]
    axis.add_patch(Rectangle((-190, -120), 380, 240, facecolor='#f5e4d5', edgecolor='#8a663d', label='380 × 240 mm carrier'))
    for x in (-93, 93):
        axis.add_patch(Rectangle((x-92, -104), 184, 184, facecolor='#d9d9d9', edgecolor='#999999'))
    for tile in unit['channel_map']:
        x, y, _ = tile['tile_center_mm']
        axis.add_patch(Rectangle((x-14.85, y-14.85), 29.7, 29.7, facecolor='#cc6600', edgecolor='white', lw=.3))
    axis.add_patch(Rectangle((-175, 85), 350, 30, facecolor='#b8c5a8', edgecolor='#738065', label='Shared service board bay'))
    axis.set(xlabel='Carrier x [mm]', ylabel='Carrier y [mm]', aspect='equal', xlim=(-205, 205), ylim=(-132, 132),
             title='72 separate scintillator cores · 30 mm pitch\n29.7 × 29.7 × 3 mm cores · actual 6.3 mm board gap')
    axis.text(0, 100, 'Shared service board bay', ha='center', va='center', fontsize=9, color='#35422a')
    fig.suptitle('nODD HCAL fit and segmentation · DES-045 prototype', fontsize=15)
    fig.supxlabel('Envelope proposal; service, magnet/muon and FCAL integration require separate validation. No engineering sign-off.', fontsize=8.5)
    for ext in ('png', 'pdf', 'svg'):
        path = out / f'hcal-fit-segmentation.{ext}'
        fig.savefig(path)
        if ext == 'svg': path.write_text('\n'.join(line.rstrip() for line in path.read_text().splitlines()) + '\n')
    plt.close(fig)
    paths = [Path(__file__), config_path, layout_path, ROOT / selected['variant_spec'],
             ROOT / 'detector/config/ecal-baseline.json', ROOT / 'tools/hcal_readout/readout.py']
    hashes = {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}
    (out / 'fit-provenance.json').write_text(json.dumps(dict(source_sha256=hashes, context='Restored warm envelopes from November18 selection; dimensioned face-normal RZ outline, not a native material scan'), indent=2)+'\n')


if __name__ == '__main__': main()
