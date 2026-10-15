"""Meaningful DES036 geometry/service/identifier negative controls."""
import contextlib
import copy
import io
import json
import math
import tempfile
import unittest
from pathlib import Path
import xml.etree.ElementTree as ET

from readout import (CONFIG, I, TUBE_Y, ID_DESCRIPTOR, bounds, box_dims, build,
                     capacity, cut, materials, parts_overlap, tube_dims,
                     validate_config, validate_cuts, validate_report)
from export import export


class CommonReadout(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.config=json.loads(CONFIG.read_text())
        cls.report,cls.materials=build()

    def config_copy(self): return copy.deepcopy(self.config)
    def report_copy(self): return copy.deepcopy(self.report)

    def test_inventory_and_separate_ownership(self):
        r=self.report
        self.assertEqual(len(r['parts']),395)
        self.assertEqual(sum(p['role']=='sensitive' for p in r['parts']),72)
        self.assertEqual(sum(p['role']=='sipm' for p in r['parts']),72)
        self.assertEqual(sum(p['role']=='direct_calibration_led' for p in r['parts']),72)
        self.assertEqual(sum(p['role']=='frontend' for p in r['parts']),2)
        self.assertEqual(sum(p['role']=='shared_interface' for p in r['parts']),1)
        self.assertAlmostEqual(sum(r['module_mass_g'].values())+r['shared_carrier_mass_g'],r['carrier_and_modules_mass_g'])
        noabs,_=build(absorber=False)
        self.assertEqual(len(noabs['parts']),394)
        self.assertEqual(noabs['carrier_and_modules_mass_g'],r['carrier_and_modules_mass_g'])
        self.assertAlmostEqual(r['mass_g']-noabs['mass_g'],380*240*30*7.85/1000)

    def test_changed_carrier_depth_drives_rear_closure_and_rail_ports(self):
        c=self.config_copy();c['carrier']['size_mm'][2]=14
        r,_=build(c);old={p['name']:p for p in self.report['parts']};new={p['name']:p for p in r['parts']}
        # The variant must build with real ports aligned through the taller rails.
        # Front components and the shared cooling plate retain their own stack.
        for name in ('carrier_front_skin','m0_t0_active','m0_t0_sipm','m0_pcb_G10','m0_chip','carrier_cold_plate','carrier_tube0'):
            self.assertEqual(new[name],old[name])
        self.assertAlmostEqual(bounds(new['carrier_rear_skin'])[2][1],14)
        self.assertAlmostEqual(bounds(new['carrier_insulation'])[2][1],13.8)
        self.assertAlmostEqual(bounds(new['carrier_yrail-1'])[2][0],.2)
        self.assertAlmostEqual(bounds(new['carrier_yrail-1'])[2][1],13.8)
        self.assertAlmostEqual(new['carrier_yrail-1']['center_mm'][2],7)
        self.assertAlmostEqual(new['carrier_yrail-1']['cuts'][0]['center_mm'][2],1.5)
        self.assertEqual(r['counts'],self.report['counts'])
        self.assertEqual(r['budgets'],self.report['budgets'])

    def test_material_host_and_package_normalization(self):
        self.assertEqual(self.materials.recipes['PSHost']['composition'],{'C':8,'H':8})
        self.assertEqual(self.materials.recipes['PSHost']['density_g_cm3'],1.06)
        for name,volumes in self.config['package_volume_fractions'].items():
            expected=sum(v*self.materials.recipes[k]['density_g_cm3'] for k,v in volumes.items())
            self.assertAlmostEqual(self.materials.recipes[name]['density_g_cm3'],expected)
            self.assertAlmostEqual(sum(self.materials.recipes[name]['composition'].values()),1)

    def test_invalid_mixture_rejected(self):
        c=self.config_copy();c['package_volume_fractions']['HCalSiPMProxy']['Silicon']=.9
        with self.assertRaisesRegex(ValueError,'volume fractions'): materials(c)

    def test_channel_ownership_and_unique_volume_identifiers(self):
        r=self.report; ids=[q['volume_id'] for q in r['channel_map']]
        self.assertEqual(len(set(ids)),72)
        for q in r['channel_map']:
            self.assertEqual(q['volume_id'] & 255,9)
            self.assertEqual(q['volume_id']>>32 & 3,q['module'])
            self.assertEqual(q['volume_id']>>34 & 63,q['sensor'])
            self.assertEqual(q['local_cell_xy'],[0,0])
        for m in r['modules']:
            self.assertEqual(len(m['connected_channels']),36)
            self.assertEqual(len(m['unused_ordinary_channels']),36)
            self.assertEqual(len(m['auxiliary_channels']),6)

    def test_auxiliary_input_cannot_be_tile_channel(self):
        r=self.report_copy();r['channel_map'][0]['channel']=72
        with self.assertRaisesRegex(ValueError,'channel role'):validate_report(r)

    def test_auxiliary_role_mutation_rejected(self):
        c=self.config_copy();c['electronics']['auxiliary_roles'][0]='ordinary'
        with self.assertRaisesRegex(ValueError,'channel ownership'):build(c)

    def test_connected_capacity_mutation_rejected(self):
        c=self.config_copy();c['electronics']['ordinary_channels']=78
        with self.assertRaisesRegex(ValueError,'channel ownership'):build(c)

    def test_duplicate_sensitive_identifier_rejected(self):
        r=self.report_copy();p=next(p for p in r['parts'] if p['name']=='m1_t0_active');p['module']=0;p['owner']='module:0'
        with self.assertRaisesRegex(ValueError,'sensitive identifiers'):validate_report(r)

    def test_continuous_power_all_channels_and_stresses(self):
        b=self.report['budgets'];self.assertEqual(b['duty'],1)
        self.assertEqual(b['powered_channels'],156)
        self.assertAlmostEqual(b['frontend_W'],156*.015)
        self.assertAlmostEqual(b['power_scenarios'][0]['LV_input_W'],(156*.015+1+2)/.9)
        for case,current in zip(b['power_scenarios'],(2e-6,1e-4,1e-3)):
            self.assertEqual(case['current_A_per_device'],current)
            self.assertAlmostEqual(case['bias_W'],72*42*current)
            self.assertAlmostEqual(case['ideal_water_g_s'],case['total_heat_W']*1000/(4180*5))
        self.assertAlmostEqual(b['separate_interface_comparison']['LV_input_saving_W'],2/.9)

    def test_hidden_duty_factor_rejected(self):
        c=self.config_copy();c['contract']['continuous_duty']=.005
        with self.assertRaisesRegex(ValueError,'hidden duty'):build(c)

    def test_latency_and_bandwidth_screen_retains_overload(self):
        b=self.report['budgets'];self.assertEqual(b['latency']['ideal_margin_samples'],12)
        self.assertAlmostEqual(b['latency']['span_us'],12.8)
        nominal,stress=b['daq']
        self.assertEqual(nominal['event_bits_per_chip'],2560)
        self.assertAlmostEqual(nominal['utilization'],.9375)
        self.assertEqual(nominal['status'],'BELOW_ARITHMETIC_CAPACITY')
        self.assertEqual(stress['utilization'],1.25)
        self.assertEqual(stress['status'],'OVERLOAD')
        self.assertEqual(b['trigger']['raw_bps_per_chip'],4*1.28e9)

    def test_insufficient_latency_rejected(self):
        c=self.config_copy();c['electronics']['latency_samples']=499
        with self.assertRaisesRegex(ValueError,'latency capacity'):build(c)

    def test_payload_capacity_mutation_rejected(self):
        c=self.config_copy();c['electronics']['payload_fraction']=1.1
        with self.assertRaisesRegex(ValueError,'normalized'):build(c)

    def test_nominal_package_led_recess_and_optical_offset(self):
        r=self.report;lookup={p['name']:p for p in r['parts']}
        self.assertEqual(bounds(lookup['m0_t0_sipm'])[2],(2.7,3.55))
        self.assertEqual(bounds(lookup['m0_t0_led'])[2],(3.1,3.6999999999999997))
        self.assertAlmostEqual(bounds(lookup['m0_t0_solder'])[2][1],3.7)
        for q in r['channel_map']:
            self.assertEqual(q['optical_center_mm'][:2],q['tile_center_mm'][:2])
            self.assertAlmostEqual(q['led_center_mm'][0]-q['tile_center_mm'][0],2.4)

    def test_maximum_sourced_package_height_back_anchored(self):
        c=self.config_copy();m=c['module'];m['sipm_size_mm'][2]=1.;m['sipm_z_mm']=m['sipm_back_mm']-.5
        r,_=build(c);p=next(p for p in r['parts'] if p['name']=='m0_t0_sipm')
        self.assertAlmostEqual(bounds(p)[2][0],2.55)
        self.assertAlmostEqual(bounds(p)[2][1],3.55)
        self.assertAlmostEqual(3.5-m['recess_depth_mm'],2.4)

    def test_out_of_tolerance_package_height_rejected(self):
        c=self.config_copy();m=c['module'];m['sipm_size_mm'][2]=1.01;m['sipm_z_mm']=m['sipm_back_mm']-1.01/2
        with self.assertRaisesRegex(ValueError,'sourced tolerance'):build(c)

    def test_old_recess_fails_maximum_package_height(self):
        c=self.config_copy();m=c['module'];m['recess_depth_mm']=.9;m['sipm_size_mm'][2]=1.;m['sipm_z_mm']=m['sipm_back_mm']-.5
        with self.assertRaisesRegex(ValueError,'physical overlap'):build(c)

    def test_reflector_clearance_rejected(self):
        c=self.config_copy();c['module']['wrap_mm']=.16
        with self.assertRaisesRegex(ValueError,'wrapped tile'):build(c)

    def test_module_overlap_rejected(self):
        c=self.config_copy();c['carrier']['board_centres_xy_mm'][1]=[-92,-12]
        with self.assertRaisesRegex(ValueError,'physical overlap'):build(c)

    def test_connector_overlap_rejected(self):
        c=self.config_copy();c['carrier']['connector_x_mm'][1]=c['carrier']['connector_x_mm'][0]
        with self.assertRaisesRegex(ValueError,'physical overlap'):build(c)

    def test_led_must_fit_opening(self):
        c=self.config_copy();c['module']['led_offset_xyz_mm'][0]=4
        with self.assertRaisesRegex(ValueError,'physical overlap'):build(c)

    def test_duplicate_shared_plate_rejected(self):
        r=self.report_copy();p=copy.deepcopy(next(p for p in r['parts'] if p['role']=='cold_plate'));p['name']+='duplicate';p['owner']='module:0';p['module']=0;r['parts'].append(p)
        with self.assertRaisesRegex(ValueError,'shared ownership'):validate_report(r)

    def test_blocked_port_rejected(self):
        c=self.config_copy();c['carrier']['port_size_mm']=1.9
        with self.assertRaisesRegex(ValueError,'physical overlap'):build(c)

    def test_short_tube_handoff_rejected(self):
        c=self.config_copy();c['carrier']['tube_length_mm']=236
        with self.assertRaisesRegex(ValueError,'blocked cooling handoff'):build(c)

    def test_disconnected_handoff_rejected(self):
        r=self.report_copy();r['services']['cooling_handoffs'][0]['centre_mm'][0]+=5
        with self.assertRaisesRegex(ValueError,'physical tube'):validate_report(r)

    def test_nonfinite_placement_rejected(self):
        r=self.report_copy();r['parts'][1]['center_mm'][0]=float('nan')
        with self.assertRaisesRegex(ValueError,'physical centre'):validate_report(r)

    def test_rotated_cylindrical_plate_capacity(self):
        p=next(p for p in self.report['parts'] if p['role']=='cold_plate')
        self.assertEqual([q['frame'] for q in p['cuts']],[TUBE_Y,TUBE_Y])
        self.assertAlmostEqual(p['volume_mm3'],376*236*3-2*math.pi*236)
        self.assertAlmostEqual(p['mass_g'],p['volume_mm3']*8.96/1000)
        validate_cuts('box',box_dims([376,236,3]),p['cuts'])

    def test_uncontained_transformed_cut_rejected(self):
        q=cut('tube',tube_dims(1,238),[0,0,0],TUBE_Y)
        with self.assertRaisesRegex(ValueError,'not contained'):validate_cuts('box',box_dims([376,236,3]),[q])

    def test_overlapping_cuts_rejected(self):
        q=cut('tube',tube_dims(1,236),[0,0,0],TUBE_Y)
        with self.assertRaisesRegex(ValueError,'cutters overlap'):validate_cuts('box',box_dims([376,236,3]),[q,copy.deepcopy(q)])

    def test_cut_or_mass_corruption_rejected(self):
        r=self.report_copy();p=next(p for p in r['parts'] if p['role']=='cold_plate');p['cuts'].pop()
        with self.assertRaisesRegex(ValueError,'capacity/mass'):validate_report(r)
        r=self.report_copy();r['parts'][0]['mass_g']*=1.1
        with self.assertRaisesRegex(ValueError,'capacity/mass'):validate_report(r)

    def test_data_trigger_connectivity_separate(self):
        s=self.report['services']; data=next(q for q in s['connectors'] if q['role']=='data')
        self.assertEqual(data['DAQ_lanes'],4);self.assertEqual(data['trigger_lanes'],8)
        links=s['links'];daq=[q for q in links if q['kind']=='DAQ'];trigger=[q for q in links if q['kind']=='trigger']
        self.assertEqual(len(daq),3);self.assertEqual(len(trigger),3)
        self.assertTrue(all('trigger' not in q['source'] for q in daq))
        self.assertTrue(all('trigger' in q['source'] for q in trigger))
        r=self.report_copy();r['services']['links'][1]['kind']='trigger'
        with self.assertRaisesRegex(ValueError,'service connectivity'):validate_report(r)

    def test_scalar_budget_corruption_rejected(self):
        r=self.report_copy();r['budgets']['power_scenarios'][0]['LV_input_W']*=.01
        with self.assertRaisesRegex(ValueError,'inconsistent service'):validate_report(r)

    def test_physical_module_seams_preserved(self):
        r=self.report;lookup={p['name']:p for p in r['parts']}
        self.assertAlmostEqual(bounds(lookup['m1_pcb_G10'])[0][0]-bounds(lookup['m0_pcb_G10'])[0][1],2)
        self.assertAlmostEqual(bounds(lookup['m1_t0_active'])[0][0]-bounds(lookup['m0_t5_active'])[0][1],6.3)
        self.assertAlmostEqual(bounds(lookup['carrier_service_pcb_G10'])[1][0]-bounds(lookup['m0_pcb_G10'])[1][1],5)

    def test_deterministic_export_and_compact_identifiers(self):
        with tempfile.TemporaryDirectory() as tmp:
            a,b=Path(tmp)/'a',Path(tmp)/'b'
            with contextlib.redirect_stdout(io.StringIO()):export(a);export(b)
            for name in ('expected.json','materials.xml','readout.xml'):
                self.assertEqual((a/name).read_bytes(),(b/name).read_bytes())
            xml=ET.parse(a/'readout.xml');self.assertEqual(xml.find('readouts/readout/id').text,ID_DESCRIPTOR)
            sensitive=[p for p in xml.findall('detectors/detector/piece') if 'sensor' in p.attrib]
            self.assertEqual(len(sensitive),72)
            self.assertEqual({(int(p.get('module')),int(p.get('sensor'))) for p in sensitive},{(i,j) for i in range(2) for j in range(36)})
            plate=next(p for p in xml.findall('detectors/detector/piece') if p.get('role')=='cold_plate')
            for q in plate.findall('cut'):
                self.assertEqual(q.get('kind'),'tube');self.assertEqual(q.get('a12'),'-1');self.assertEqual(q.get('a21'),'1')


if __name__=='__main__':unittest.main()
