"""Synthetic controls for geometry-aware muon accounting; no transport evidence."""
from collections import defaultdict
from types import SimpleNamespace
import importlib.util
import unittest
from unittest.mock import patch

import numpy as np

import nodd_muon_response as m


class Hit:
    def __init__(self, cid): self.cid = cid
    def getCellID(self): return self.cid


class Contribution:
    def __init__(self, energy): self.energy = energy
    def getEnergy(self): return self.energy


def crossing(cid, pure=True, energy=1):
    return Hit(cid), [Contribution(energy)], pure, {}


class MuonAccountingTests(unittest.TestCase):
    def test_physical_module16_crosswalk_and_collision_control(self):
        descriptor = m.Descriptor("system:8,barrel:3,module:4,stave:1,layer:6,slice:5,x:32:-16,y:-16")
        class Vector(list):
            def emplace_back(self, name, value): self.append((name, value))
        root = SimpleNamespace(std=SimpleNamespace(vector=lambda name: Vector))
        calls = []
        # Recorded native IDDescriptor-only fixture: module16 -> module0,
        # with no carry into stave/layer; no local production masking is used.
        class Spec:
            def encode(self, pairs):
                fields = dict(pairs); calls.append(fields)
                self.asserted = fields["module"] in (0, 16)
                return 65544
            def decoder(self):
                return SimpleNamespace(get=lambda encoded, name: descriptor.decode(encoded)[name])
        spec = Spec(); crosswalk = {}
        physical = dict(system=8, barrel=0, module=16, layer=1)
        key = m.register_physical_plane("odd-zero", "ECalBarrelCollection", physical, spec, descriptor, root, crosswalk)
        self.assertEqual(calls, [physical])
        self.assertEqual(key, ("ECalBarrelCollection", 0, 0, 1))
        self.assertEqual(crosswalk[key]["physical_ids"]["module"], 16)
        self.assertEqual(crosswalk[key]["decoded_fields"]["module"], 0)
        self.assertEqual(crosswalk[key]["decoded_fields"]["stave"], 0)
        self.assertEqual(set(crosswalk[key]["decoded_fields"]), set(descriptor.fields))
        with self.assertRaisesRegex(ValueError, "collision"):
            m.register_physical_plane("odd-zero", "ECalBarrelCollection", dict(physical, module=0), spec, descriptor, root, crosswalk)

    @unittest.skipUnless(importlib.util.find_spec("ROOT") and importlib.util.find_spec("dd4hep"), "Requires installed ROOT/DD4hep runtime; descriptor-only control")
    def test_actual_native_module1_through16_encoding(self):
        import ROOT
        import dd4hep  # Loads DDCore dictionaries; no geometry construction.
        text = "system:8,barrel:3,module:4,stave:1,layer:6,slice:5,x:32:-16,y:-16"
        descriptor = m.Descriptor(text)
        spec = ROOT.dd4hep.IDDescriptor("nodd_muon_module16_control", text)
        crosswalk = {}
        for module in range(1, 17):
            physical = dict(system=8, barrel=0, module=module, layer=1)
            key = m.register_physical_plane("odd-zero", "ECalBarrelCollection", physical, spec, descriptor, ROOT, crosswalk)
            self.assertEqual(key[2], module if module < 16 else 0)
            self.assertEqual(crosswalk[key]["decoded_fields"]["stave"], 0)
            self.assertEqual(crosswalk[key]["decoded_fields"]["layer"], 1)
        self.assertEqual(len(crosswalk), 16)

    def test_population_accessor_is_required_and_invalid_manager_fails_closed(self):
        # The synthetic composed-root detector's direct getter is unavailable.
        # Only the public population accessor supplies a valid lookup handle.
        detector = object(); manager = SimpleNamespace(isValid=lambda: True)
        calls = []
        def populate(actual):
            calls.append(actual)
            return manager
        dd4hep = SimpleNamespace(VolumeManager=SimpleNamespace(getVolumeManager=populate))
        self.assertIs(m.populated_volume_manager(detector, dd4hep), manager)
        self.assertEqual(calls, [detector])
        manager.isValid = lambda: False
        with self.assertRaisesRegex(RuntimeError, "population failed"):
            m.populated_volume_manager(detector, dd4hep)

    def test_full_width_signed_descriptors_and_explicit_offsets(self):
        descriptor = m.Descriptor("system:8,barrel:3,module:4,stave:1,layer:6,slice:5,x:32:-16,z:-16")
        # Set high signed z=-2 and x=-3 without converting via float.
        cid = 8 | (2 << 8) | (7 << 11) | (48 << 16) | (65533 << 32) | (65534 << 48)
        decoded = descriptor.decode(cid)
        self.assertEqual(decoded["x"], -3); self.assertEqual(decoded["z"], -2)
        self.assertEqual(m.plane_key("odd-zero", "ECalEndcapCollection", decoded), ("ECalEndcapCollection", 2, 7, 48))
        self.assertGreater(cid, 2**53)
        with self.assertRaisesRegex(ValueError, "Overlapping"):
            m.Descriptor("a:8,b:4:8")

    def test_region_side_layer_controls_do_not_apply_odd_layout_to_nodd(self):
        descriptor = m.Descriptor("system:8,side:2,sector:4,layer:6,module:10,x:-6,y:-6")
        cid = 9 | (2 << 8) | (15 << 10) | (47 << 14) | (551 << 20) | (63 << 30)
        fields = descriptor.decode(cid)
        self.assertEqual(fields["x"], -1)
        self.assertEqual(m.plane_key("nodd", "EDGEHits", fields), ("EDGEHits", 2, 15, 47))
        with self.assertRaisesRegex(ValueError, "side"):
            m.plane_key("nodd", "BARRELHits", fields)
        with self.assertRaisesRegex(ValueError, "layer"):
            m.plane_key("nodd", "EDGEHits", dict(fields, layer=48))
        with self.assertRaisesRegex(ValueError, "descriptor"):
            descriptor.decode(cid | (1 << 63))

    def test_actual_thin_axis_and_material_prefix_controls(self):
        self.assertEqual(m.thin_axis([44, 44, .25]), 2)
        self.assertEqual(m.thin_axis([100, .25, 1100]), 1)
        for extents in ([44, 44, .3], [.25, .25, 100], [44, 0, .25]):
            with self.assertRaises(ValueError): m.thin_axis(extents)
        self.assertTrue(m.silicon_name("B_Silicon"))
        self.assertTrue(m.silicon_name("Silicon"))
        self.assertFalse(m.silicon_name("SiliconGuardComposite"))

    def test_physical_adjacency_never_bridges_missing_observed_plane(self):
        keys = [("EDGEHits", 1, 0, layer) for layer in range(5)]
        inventory = set(keys)
        self.assertEqual(m.physical_neighbors(keys[2], inventory), (keys[1], keys[3]))
        # Observed layer 4 cannot replace missing immediate layer 3.
        centers = {keys[0]: [0, 0, 0], keys[1]: [0, 0, 1], keys[2]: [0, 0, 2], keys[4]: [0, 0, 4]}
        cosine, reason = m.chord_qualification(keys[2], centers, inventory, [0, 0, 1])
        self.assertIsNone(cosine); self.assertEqual(reason, "chord_unavailable")
        centers[keys[3]] = [0, 0, 3]
        self.assertEqual(m.chord_qualification(keys[2], centers, inventory, [0, 0, 1]), (1., None))
        self.assertEqual(m.chord_qualification(keys[0], centers, inventory, [0, 0, 1])[1], "endpoint")
        self.assertEqual(m.chord_qualification(keys[2], centers, inventory, [1, 0, 0])[1], "incidence_rejected")

    def test_split_uses_any_cell_strict_threshold_and_one_depth_trial(self):
        depths = {0: [crossing(101), crossing(102)], 2: [crossing(103, pure=False)]}
        signed = {mode: {101: .4, 102: .4, 103: float(np.float32(.6))} for mode in ("off", "on")}
        counts, den, counters = m.depth_trials(depths, {0, 1, 2}, signed)
        self.assertEqual(den["identified"], 2); self.assertEqual(den["identified_split"], 1)
        self.assertEqual(counters["missing_primary_layer_unknown_crossing"], 1)
        self.assertEqual(counters["contaminated_identified_layer"], 1)
        # Two .4 pulses do not pass .6. Exact stored float32 .6 also fails.
        self.assertEqual(counts["identified"][:, 3].tolist(), [0, 0])
        self.assertEqual(counts["identified"][:, 0].tolist(), [2, 2])
        depths[3] = [crossing(104)]
        with self.assertRaisesRegex(ValueError, "inventory"):
            m.depth_trials(depths, {0, 1, 2}, signed)

    def test_zero_signal_identified_is_distinct_from_missing_unknown(self):
        counts, den, counters = m.depth_trials({0: [crossing(1, energy=0)]}, {0, 1},
                                               {mode: {1: 0.} for mode in ("off", "on")})
        self.assertEqual(counters["known_zero_identified_primary_signal"], 1)
        self.assertEqual(counters["missing_primary_layer_unknown_crossing"], 1)
        self.assertEqual(den["identified"], 1)
        self.assertEqual(int(counts["identified"].sum()), 0)

    def test_nominal_and_conditional_denominators_and_shared_covariance(self):
        counts = np.zeros((2, 2, len(m.THRESHOLDS)), int)
        counts[1] = 1
        indices = np.array([[0, 0], [0, 1], [1, 1], [1, 0]])
        nominal = m.crossing_statistics(counts, [3, 3], indices)
        conditional = m.crossing_statistics(counts, [1, 1], indices)
        self.assertEqual(nominal["denominator"], 6)
        self.assertEqual(conditional["denominator"], 2)
        self.assertAlmostEqual(nominal["efficiency"][0][0], 1/6)
        self.assertEqual(conditional["efficiency"][0][0], .5)
        # Same event indices preserve correlations between modes/thresholds.
        self.assertGreater(conditional["joint_covariance"][0][-1], 0)
        self.assertEqual(conditional["joint_covariance"][0][0], conditional["joint_covariance"][0][-1])

    def test_undefined_category_bootstrap_is_retained_not_conditioned_away(self):
        counts = np.zeros((2, 2, len(m.THRESHOLDS)), int)
        indices = np.array([[0, 0], [0, 1], [1, 1]])
        result = m.crossing_statistics(counts, [0, 1], indices)
        self.assertEqual(result["event_cluster_bootstrap_undefined_replicates"], 1)
        self.assertIsNone(result["event_cluster_bootstrap_SE"])
        self.assertIsNone(result["event_cluster_bootstrap_CI95"])
        self.assertTrue(all(value is None for row in result["joint_covariance"] for value in row))
        self.assertGreater(result["conditional_crossing_Wilson95"][1][0][0], 0)
        empty = m.crossing_statistics(counts, [0, 0], indices)
        self.assertIsNone(empty["efficiency"])
        self.assertEqual(empty["conditional_crossing_Wilson95"], [None, None])

    def test_pinned_helpers_are_used_without_changing_legacy_files(self):
        fitter, response = m.helpers()
        self.assertEqual(m.sha(fitter.__file__), m.HELPERS["muon_response"])
        self.assertEqual(m.sha(response.__file__), m.HELPERS["digitized_response"])

    def test_sparse_fixed_fit_returns_explicit_unavailable_spectrum(self):
        fitter, response = m.helpers()
        def unavailable(*args, **kwargs): raise RuntimeError("synthetic empty fixed-model fit")
        with patch.object(fitter, "fit_landau_gaussian", side_effect=unavailable):
            result = m.fit_spectra({s: [[], []] for s in m.STAGES}, {"off": [], "on": []}, 126100, "synthetic", 1)
        for stage in m.STAGES:
            self.assertEqual(result[stage]["histogram"]["entries"], 0)
            self.assertEqual(result[stage]["fit"]["fit_range_MIP"], [.25, 2.5])
            self.assertEqual(result[stage]["fit"]["status"], "unavailable")
            self.assertIsNone(result[stage]["fit"]["underlying_Landau_MPV"])
        self.assertEqual(result["on"]["actual_thresholded_output"]["entries"], 0)

    def test_empty_descriptives_preserve_nulls_and_no_nan(self):
        self.assertIsNone(m.basic([])["mean"])
        self.assertIsNone(m.basic([0])["SD"])
        self.assertIsNone(m.basic([0, 0])["RMS_over_mean"])
        with self.assertRaises(ValueError): m.basic([np.nan])


if __name__ == "__main__": unittest.main()
