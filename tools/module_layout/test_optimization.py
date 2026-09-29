"""Controls for placement constraints and selection leakage in DES-011."""
import copy
import json
from pathlib import Path
import unittest

try:
    from .optimization import MODES, SUBS, disc_coordinates, no_mean_hit_loss, select, validate_config
except ImportError:
    from optimization import MODES, SUBS, disc_coordinates, no_mean_hit_loss, select, validate_config


class OptimizationDriverTests(unittest.TestCase):
    def test_unsupported_models_duplicate_scans_and_leaked_seed_rejected(self):
        config=json.loads(Path(__file__).with_name("optimization_config.json").read_text())
        validate_config(config)
        for key,value in (("variant","flat"),("pixel_family","single"),
                          ("pixel_trunk_inner_mm",[170.,170.]),("disc_spacing",["typo"])):
            changed=copy.deepcopy(config);changed[key]=value
            with self.assertRaises(ValueError):validate_config(changed)
        config["holdout"]["seed"]=config["training"]["seed"]
        with self.assertRaises(ValueError):validate_config(config)

    def test_ordered_signed_disc_schedule_respects_first_and_last(self):
        layout = {"layers": []}
        constraints = {side: {} for side in ("negative", "positive")}
        for side, sign in (("negative", -1), ("positive", 1)):
            for sub in SUBS:
                constraints[side][sub] = {"minimum_first_disc_center_abs_z_mm": 600.}
                for i, z in enumerate((700., 1600., 3000.)):
                    layout["layers"].append(dict(id=f"{side}-{sub}-{i}",kind="disc",subsystem=sub,z_m=sign*z/1000))
        for pattern in ("inherited", "uniform", "front_loaded"):
            coords = disc_coordinates(layout,constraints,pattern,1.25)
            for side in constraints:
                for sub in SUBS:
                    positions = [coords[f"{side}-{sub}-{i}"] for i in range(3)]
                    self.assertEqual(positions[0],600.)
                    self.assertEqual(positions[-1],3000.)
                    self.assertLess(positions[0],positions[1])
                    self.assertLess(positions[1],positions[2])
        constraints["positive"]["pixel"]["minimum_first_disc_center_abs_z_mm"] = 3001.
        with self.assertRaises(ValueError):
            disc_coordinates(layout,constraints,"uniform",1.25)

    def test_more_area_or_total_hits_cannot_hide_subsystem_mean_loss(self):
        baseline = {mode: {"per_subdetector": {sub:{"stations":{"mean":4.}} for sub in SUBS}} for mode in MODES}
        candidate = copy.deepcopy(baseline)
        self.assertTrue(no_mean_hit_loss(candidate,baseline))
        candidate["positive"]["per_subdetector"]["pixel"]["stations"]["mean"] = 3.9
        candidate["positive"]["per_subdetector"]["short_strip"]["stations"]["mean"] = 8.
        self.assertFalse(no_mean_hit_loss(candidate,baseline))

    def test_selection_rejects_infeasible_or_hit_losing_high_area_case(self):
        def record(name,area,hits,gap,feasible=True,guard=True):
            return dict(id=name,feasible=feasible,no_subsystem_mean_hit_loss=guard,
                        score=dict(active_area_m2=area,mean_stations=hits,
                                   worst_mode_mean_stations=hits,
                                   worst_mode_p95_inter_station_gap_mm=gap,
                                   worst_mode_p95_boundary_gap_mm=gap))
        records=[record("coverage",10,10,100),record("spacing",11,9,80),
                 record("impossible",100,100,1,False),record("loses_hits",200,99,2,True,False)]
        chosen=select(records)
        self.assertEqual(chosen,dict(coverage="coverage",spacing="spacing",area="spacing"))
        self.assertEqual(chosen,select(list(reversed(records))))
        control=record("large_original_pockets",300,200,0.5)
        control["parameters"]={"original_pocket_floors":True}
        self.assertEqual(chosen,select(records+[control]))
        with self.assertRaises(RuntimeError):select(records[2:])


if __name__=="__main__":unittest.main()
