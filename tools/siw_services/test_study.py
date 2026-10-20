"""Physical negative controls for the service-envelope proposal."""
import copy
import json
from pathlib import Path
import unittest
from study import study


class EnvelopeControls(unittest.TestCase):
    def setUp(self):
        self.data = json.loads(Path(__file__).with_name("inputs.json").read_text())

    def test_nominal_and_adverse_merger(self):
        r = study(self.data)
        self.assertAlmostEqual(r["total_water_flow_kg_s"], 12.413991148325359)
        self.assertGreater(r["merged_station_each_end"]["adverse_area_mm2"], 135000)
        self.assertLess(r["merged_station_each_end"]["adverse_area_mm2"], 193600)

    def reject(self, **choices):
        d = copy.deepcopy(self.data)
        d["choices"].update(choices)
        with self.assertRaises(ValueError):
            study(d)

    def test_old_30_mm_rear_gap_cannot_host_turn(self):
        self.reject(rear_axial_gap_mm=30)

    def test_polygon_corner_cannot_be_treated_as_apothem(self):
        self.reject(service_inner_radius_mm=2255)

    def test_lanes_cannot_overlap_sector_edges(self):
        self.reject(lane_tangent_mm=1000)

    def test_adverse_cables_do_not_fit_700_mm_lane(self):
        self.reject(lane_tangent_mm=700)

    def test_individual_lane_is_not_merged_capacity(self):
        self.reject(junction_radial_mm=150)

    def test_forward_reservation_cannot_enter_HCAL(self):
        self.reject(forward_outer_radius_mm=310)

    def test_LAr_upstream_collar_cannot_overlap_SiW_endcap(self):
        self.reject(forward_front_clearance_mm=-83.2)

    def test_feed_inventory_and_voltage_use_same_loop(self):
        r = study(self.data)
        end, barrel = r["endcap_each"], r["barrel"]
        end_resistance = end["power_loop_drop_V"] / end["input_current_A_per_station"]
        barrel_resistance = barrel["power_loop_drop_V"] / barrel["input_current_A_per_station"]
        self.assertAlmostEqual(end_resistance/barrel_resistance,24/40)
        self.assertAlmostEqual(end["power_copper_kg"],172.032)

    def test_passive_interface_boards_are_not_powered_chips(self):
        d = copy.deepcopy(self.data)
        d["source_facts"]["barrel_powered_interfaces"] = 22560
        with self.assertRaises(ValueError):
            study(d)


if __name__ == "__main__":
    unittest.main()
