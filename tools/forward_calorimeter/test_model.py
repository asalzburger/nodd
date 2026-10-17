"""Adverse controls and independent physical conservation checks for DES039."""
from copy import deepcopy
import json
import math
import unittest
from study import canonical_report
from model import (HERE, build, collar_config, fibre_endpoint, fibre_id, inventory,
                   intervals, load_config, ray_sample, routing, service_screen,
                   thermal, validate_config)


class ForwardCalorimeter(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.config=load_config();cls.model=build(cls.config)
        cls.collar=build(collar_config(cls.config))
        cls.contexts=json.loads((HERE/'layout-contexts.json').read_text())

    def test_package_closure_and_adverse_radial_nesting(self):
        c=deepcopy(self.config);c['module']['length_mm']+=1
        with self.assertRaisesRegex(ValueError,'close'):validate_config(c)
        c=deepcopy(self.config);c['module']['bore_radius_mm']=60
        with self.assertRaisesRegex(ValueError,'nesting'):validate_config(c)

    def test_finite_fibres_and_non_overlapping_lattice(self):
        for model in (self.model,self.collar):
            c=model['config'];m,f=c['module'],c['fibres'];seen=set()
            for v in model['fibres']:
                self.assertNotIn((v['i'],v['j']),seen);seen.add((v['i'],v['j']))
                r=math.hypot(v['x_mm'],v['y_mm'])
                self.assertGreater(r-f['hole_radius_mm'],m['sampling_inner_radius_mm'])
                self.assertLess(r+f['hole_radius_mm'],m['sampling_outer_radius_mm'])
                self.assertGreaterEqual(v['z0_mm'],model['zones_mm']['sampling'][0])
            self.assertGreater(f['pitch_mm'],2*f['hole_radius_mm'])

    def test_exclusive_sampling_volume_conservation(self):
        for model in (self.model,self.collar):
            i=inventory(model);v=i['volumes_mm3']
            self.assertAlmostEqual(sum(v[k] for k in ('tungsten','fused_silica','buffer_proxy','air_insertion_gap')),i['sampling_envelope_volume_mm3'],places=5)
            f=model['config']['fibres'];m=model['config']['module']
            holes=math.pi*f['hole_radius_mm']**2*sum(x['z1_mm']-x['z0_mm'] for x in model['fibres'])
            self.assertAlmostEqual(i['sampling_envelope_volume_mm3']-v['tungsten'],holes,places=5)
            # W plugs ahead of short fibres reduce the bore volume versus two full populations.
            full=math.pi*f['hole_radius_mm']**2*len(model['fibres'])*(model['zones_mm']['sampling'][1]-model['zones_mm']['sampling'][0])
            self.assertLess(holes,full)

    def test_pixel_occupancy_and_ferrule_endpoints(self):
        for model in (self.model,self.collar):
            bins={}
            for f in model['fibres']:
                key=(f['channel'],f['pixel']);bins[key]=bins.get(key,0)+1
                x,y=fibre_endpoint(model,f);ch=model['channels'][f['channel']]
                a=ch['phi_rad'];dr=(x-ch['x_mm'])*math.cos(a)+(y-ch['y_mm'])*math.sin(a)
                dt=-(x-ch['x_mm'])*math.sin(a)+(y-ch['y_mm'])*math.cos(a)
                px=(f['pixel']%4-1.5)*6.2;py=(f['pixel']//4-1.5)*6.2
                self.assertLess(abs(dr-px)+.4,3.)
                self.assertLess(abs(dt-py)+.4,3.)
            self.assertLessEqual(max(bins.values()),25)

    def test_sensor_and_pipe_intrusion_controls(self):
        c=deepcopy(self.config);c['readout']['cartridge_side_mm']=40
        with self.assertRaises(ValueError):validate_config(c)
        c=deepcopy(self.config);c['thermal']['pipe_radius_mm']=287
        with self.assertRaisesRegex(ValueError,'housing'):validate_config(c)
        c=deepcopy(self.config);c['collar']['neck_outer_radius_mm']=302
        with self.assertRaisesRegex(ValueError,'calorimeter'):service_screen(c,self.contexts)

    def test_sampled_routing_and_adverse_short_fanout(self):
        for model in (self.model,self.collar):
            self.assertGreater(routing(model)['sampled_minimum_bend_radius_mm'],70)
        bad=deepcopy(self.model);lo,hi=bad['zones_mm']['fanout'];bad['zones_mm']['fanout']=(lo,lo+80.)
        with self.assertRaisesRegex(ValueError,'bend'):routing(bad)

    def test_signed_side_material_symmetry(self):
        for phi in (.11,.37,.81,1.71):
            a=ray_sample(self.model,4.5,phi,4553.2,1)
            b=ray_sample(self.model,4.5,-phi,4553.2,-1)
            self.assertEqual(a,b)
            self.assertGreaterEqual(a['nuclear_lambda'],0)
            total=sum(a['paths_mm'].values())
            interval=intervals(4553.2,5753.2,55.,270.,4.5)
            self.assertAlmostEqual(total,(interval[1]-interval[0])*math.cosh(4.5)/math.sinh(4.5),places=8)

    def test_zero_matrix_seam_and_original_aperture_controls(self):
        ray=ray_sample(self.model,4.,math.pi/2,4553.2)
        self.assertEqual(ray['nuclear_lambda'],0)
        self.assertGreater(ray['paths_mm']['seam_air'],1200)
        self.assertIsNone(intervals(4553.2,5753.2,80.,270.,5.))
        self.assertIsNotNone(intervals(4553.2,5753.2,55.,270.,5.))

    def test_ids_distinguish_components_and_sides(self):
        seen=set()
        for model in (self.model,self.collar):
            for side in (-1,1):
                for f in model['fibres']:
                    ident=fibre_id(model,f,side)
                    self.assertNotIn(ident,seen);seen.add(ident)
                    self.assertEqual((ident>>32)&255,10)
                    self.assertEqual((ident>>30)&3,1 if side>0 else 2)
                    self.assertEqual((ident>>22)&1,int(model['config'].get('component')=='collar'))
                    self.assertEqual(ident&65535,f['index'])

    def test_report_format_preserves_counts_and_rejects_physical_changes(self):
        sample={'path_mm':1234.56789012345,'count':24324,'source':'exact-hash'}
        low_bit=dict(sample,path_mm=math.nextafter(sample['path_mm'],math.inf))
        self.assertEqual(canonical_report(sample),canonical_report(low_bit))
        physical=dict(sample,path_mm=sample['path_mm']+.001)
        self.assertNotEqual(canonical_report(sample),canonical_report(physical))
        self.assertEqual(canonical_report(sample)['count'],24324)
        self.assertEqual(canonical_report(sample)['source'],'exact-hash')
        with self.assertRaisesRegex(ValueError,'Non-finite'):
            canonical_report({'invalid':float('nan')})

    def test_conversion_and_flow_conserve_heat(self):
        t=thermal(self.model);c=self.config['thermal']
        for scenario in ('nominal','stress'):
            v=t[scenario]
            self.assertAlmostEqual(v['local_heat_per_end_w']*c['conversion_efficiency'],v['detector_subtotal_w'])
            self.assertAlmostEqual(v['ideal_water_flow_per_end_kg_s']*c['coolant_cp_j_per_kg_k']*c['coolant_rise_k'],v['local_heat_per_end_w'])
        self.assertGreater(t['stress']['local_heat_per_end_w'],t['nominal']['local_heat_per_end_w'])


if __name__=='__main__':unittest.main()
