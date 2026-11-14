"""Conservation, miter, transform and failure controls for isolated route models."""
from copy import deepcopy
from contextlib import redirect_stdout
import io
import json
import math
from pathlib import Path
import tempfile
import unittest

from routing import CONFIG, ROOT, add, build, cross, dot, scale, segments, sha, sub
from routing_native import inputs
from routing_transport import audit as transport_audit, cases


class RoutingControls(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.config = json.loads(CONFIG.read_text())
        cls.old, _ = build('old'); cls.new, _ = build('new')

    def test_common_endpoints_analytic_lengths_and_constituent_references(self):
        self.assertEqual(self.old['material_totals'], self.new['material_totals'])
        for data in (self.old, self.new):
            self.assertAlmostEqual(data['analytic_length_mm'], 4968.343720697463, places=9)
            self.assertAlmostEqual(data['material_totals']['lArCaloSteel']['volume_mm3_per_route'], 296561.73053559044, places=6)
            self.assertAlmostEqual(data['material_totals']['PrototypeNitrogenTwoPhase']['volume_mm3_per_route'], 1264289.4828096223, places=6)
            self.assertEqual(data['route_count'], 32)
        for old, new in zip(self.old['paths'], self.new['paths']):
            self.assertEqual(old['vertices_mm'][0], new['vertices_mm'][0])
            self.assertEqual(old['vertices_mm'][-1], new['vertices_mm'][-1])

    def test_adjusted_annular_and_core_volumes_equal_references(self):
        for data in (self.old, self.new):
            inner, outer = data['adjusted_radii_mm']['inner'], data['adjusted_radii_mm']['outer']
            steel = math.pi*(outer*outer-inner*inner)*data['polyline_length_mm']
            core = math.pi*inner*inner*data['polyline_length_mm']
            self.assertAlmostEqual(steel, data['material_totals']['lArCaloSteel']['volume_mm3_per_route'], places=7)
            self.assertAlmostEqual(core, data['material_totals']['PrototypeNitrogenTwoPhase']['volume_mm3_per_route'], places=7)

    def test_all_proper_frames_and_shared_opposite_join_planes(self):
        for path in self.new['paths']:
            for segment in path['segments']:
                frame = segment['frame']
                self.assertAlmostEqual(dot(cross(frame[0], frame[1]), frame[2]), 1, places=12)
                for i in range(3):
                    for j in range(3): self.assertAlmostEqual(dot(frame[i], frame[j]), float(i == j), places=12)
                self.assertGreater(segment['minimum_full_disk_thickness_mm'], 0)
                point = add(segment['center_mm'], scale(frame[2], segment['length_mm']/2))
                self.assertLess(math.dist(point, path['vertices_mm'][segment['index']+1]), 1e-9)
            for before, after in zip(path['segments'], path['segments'][1:]):
                self.assertLess(math.sqrt(dot(add(before['high_normal_global'], after['low_normal_global']), add(before['high_normal_global'], after['low_normal_global']))), 1e-12)

    def test_resolution_converges_without_changing_material(self):
        values = []
        for step in (10, 5, 2.5):
            config = deepcopy(self.config); config['arc_step_deg'] = step
            model, _ = build('new', config)
            self.assertEqual(model['material_totals'], self.new['material_totals'])
            values.append(model)
        self.assertGreater(values[0]['radius_scale'], values[1]['radius_scale'])
        self.assertGreater(values[1]['radius_scale'], values[2]['radius_scale'])
        self.assertLess(values[1]['max_sagitta_mm'], values[0]['max_sagitta_mm']/3.9)
        self.assertLess(values[2]['max_sagitta_mm'], values[1]['max_sagitta_mm']/3.9)
        self.assertAlmostEqual(values[1]['polyline_length_mm'], 4967.953085169159, places=9)

    def test_cables_and_jackets_never_enter_material_inventory(self):
        self.assertFalse(self.new['empty_envelopes']['materialised'])
        self.assertTrue(self.new['empty_envelopes']['excluded_from_material_inventory'])
        self.assertEqual(set(self.new['materials']), {'lArCaloSteel', 'PrototypeNitrogenTwoPhase'})
        self.assertEqual(set(self.new['material_totals']), set(self.new['materials']))

    def test_degenerate_and_reversing_segments_are_rejected(self):
        for points in ([[0, 0, 0], [0, 0, 0]], [[0, 0, 0], [0, 0, 1], [0, 0, 0]]):
            with self.assertRaisesRegex(ValueError, 'Degenerate'): segments(points, 0.)

    def test_invalid_route_and_resolution_parameters_are_rejected(self):
        for key, value in [('arc_step_deg', 0), ('arc_step_deg', 31), ('arc_step_deg', float('nan')),
                           ('handoff_radius_mm', 3000), ('stations_each_side', 0), ('cold_radius_mm', 2700)]:
            config = deepcopy(self.config); config[key] = value
            with self.subTest(key=key, value=value), self.assertRaises(ValueError): build('new', config)
        config = deepcopy(self.config); config['s_bend_start_abs_z_mm']['new'] = config['upstream_abs_z_mm']
        with self.assertRaises(ValueError): build('new', config)
        with self.assertRaises(ValueError): build('other')

    def test_selected_existing_pipe_material_hypothesis_is_fixed(self):
        services = json.loads((CONFIG.parent/'services.json').read_text()); services['nitrogen_pipe_od_mm'] = 21
        with self.assertRaisesRegex(ValueError, 'construction'): build('new', services=services)

    def test_joint_probes_cover_both_materials_and_signed_ends(self):
        points = self.new['joint_probes']
        self.assertEqual(len(points), 32*42*4)
        self.assertEqual({p['sign'] for p in points}, {-1, 1})
        self.assertEqual({p['material'] for p in points}, set(self.new['materials']))
        self.assertEqual({p['path'].split('_')[1] for p in points}, {'m', 'p'})
        self.assertEqual({c['label'] for c in cases(self.new)}, {'transverse', 'core_miter', 'wall_miter'})

    def test_source_and_material_bindings_reject_changed_artifacts(self):
        parent = ROOT/'build/lar-routing/softeng'; parent.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(dir=parent) as tmp:
            directory = Path(tmp); compact = directory/'routing.xml'; compact.write_text('<test_fixture/>')
            (directory/'materials.xml').write_text('<materials/>')
            proof = {'source_sha256': {'tools/lar_calorimeter/routing.py': sha(CONFIG.with_name('routing.py'))},
                     'artifact_sha256': {p.name:sha(p) for p in (compact, directory/'materials.xml')}}
            expected = directory/'expected.json'; expected.write_text(json.dumps(proof))
            inputs(compact, expected)
            (directory/'materials.xml').write_text('changed')
            with self.assertRaisesRegex(ValueError, 'Stale routing artifact'): inputs(compact, expected)


class TransportReadbackControls(unittest.TestCase):
    def fixture(self, directory, mutate=None):
        requests = [dict(label=label, run=i, position_mm=[0,0,0], direction=[1,0,0], route_name='route_p_0', target_joint=6 if i else None)
                    for i,label in enumerate(('transverse','core_miter','wall_miter'))]
        steps = []
        for case in requests:
            materials = ['PrototypeNitrogenTwoPhase','lArCaloSteel'] if case['run'] == 0 else ['PrototypeNitrogenTwoPhase'] if case['run'] == 1 else ['lArCaloSteel']
            for i, material in enumerate(materials):
                kind = 'core' if material == 'PrototypeNitrogenTwoPhase' else 'wall'
                steps.append(dict(run=case['run'], event=0, track=1, parent=0, pdg=0, vertex_mm=[0,0,0],
                    pre_momentum_GeV=[1,0,0], pre_kinetic_energy_GeV=1., step_mm=1., pre_mm=[i,0,0],post_mm=[i+1,0,0],
                    pre_material=material, post_material=material if case['run'] else 'Air',
                    pre_volume='route_p_0_s6_'+kind, post_volume='route_p_0_s7_'+kind, geometry_boundary=True))
        if mutate: mutate(steps)
        (directory/'cases.json').write_text(json.dumps(requests))
        (directory/'steps.jsonl').write_text('\n'.join(json.dumps(s) for s in steps)+'\n')
        (directory/'conversion.json').write_text('{"status":"PASS","scope":"test fixture"}')
        (directory/'transport.log').write_text('test fixture')
        for case in requests: (directory/(case['label']+'.root')).write_text('non-event diagnostic fixture')
        receipt = dict(exit_code=0,inputs_unchanged=True)
        for filename,key in [('cases.json','cases_sha256'),('steps.jsonl','steps_sha256'),('conversion.json','conversion_sha256'),('transport.log','log_sha256')]:
            receipt[key]=sha(directory/filename)
        (directory/'receipt.json').write_text(json.dumps(receipt))

    def temporary(self):
        parent=ROOT/'build/lar-routing/softeng';parent.mkdir(parents=True,exist_ok=True)
        return tempfile.TemporaryDirectory(dir=parent)

    def test_native_jsonl_supports_passive_no_event_root_evidence(self):
        with self.temporary() as tmp, redirect_stdout(io.StringIO()):
            directory=Path(tmp);self.fixture(directory);proof=transport_audit(directory)
        self.assertEqual(proof['events'],3);self.assertEqual(proof['miter_crossings'],2)
        self.assertIn('do not produce EDM4hep event frames',proof['saved_event_format'])

    def test_wrong_observed_primary_energy_is_rejected(self):
        with self.temporary() as tmp:
            directory=Path(tmp);self.fixture(directory,lambda rows: rows[0].update(pre_kinetic_energy_GeV=2.))
            with self.assertRaisesRegex(ValueError,'identity/energy'): transport_audit(directory)

    def test_missing_wall_transport_is_rejected(self):
        with self.temporary() as tmp:
            directory=Path(tmp)
            def remove_wall(rows): rows[:]=[r for r in rows if not(r['run']==0 and r['pre_material']=='lArCaloSteel')]
            self.fixture(directory,remove_wall)
            with self.assertRaisesRegex(ValueError,'wall and core'): transport_audit(directory)

    def test_wrong_adjacent_miter_does_not_satisfy_aimed_joint(self):
        with self.temporary() as tmp:
            directory=Path(tmp)
            def different_joint(rows):
                for row in rows:
                    if row['run']==1: row.update(pre_volume='route_p_0_s5_core',post_volume='route_p_0_s6_core')
            self.fixture(directory,different_joint)
            with self.assertRaisesRegex(ValueError,'aimed shared miter'): transport_audit(directory)

    def test_extra_native_events_are_rejected(self):
        with self.temporary() as tmp:
            directory=Path(tmp)
            def extra_event(rows): rows.append(dict(rows[-1],run=3))
            self.fixture(directory,extra_event)
            with self.assertRaisesRegex(ValueError,'event set'): transport_audit(directory)

    def test_changed_raw_steps_are_rejected(self):
        with self.temporary() as tmp:
            directory=Path(tmp);self.fixture(directory);(directory/'steps.jsonl').write_text('changed')
            with self.assertRaisesRegex(ValueError,'Changed smoke artifact'): transport_audit(directory)


if __name__ == '__main__': unittest.main()
