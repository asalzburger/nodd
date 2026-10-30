"""Matching/denominator controls, including native matcher omission hazards."""
import copy
from pathlib import Path
import sys
import unittest
import tempfile
import json

sys.path.insert(0,str(Path(__file__).resolve().parent))
from analyze import ambiguity_shared_max, classify_event, interval, rate, summarize
from select_profile import select

PRIMARY=[1,0,1,0,0]
SECONDARY=[1,0,1,1,0]
CONFIG={"matching":{"purity":.5,"completeness":.5,"reconstructable_measurements":6,"reconstructable_pixel_groups":3},
        "quality":{"minimum_measurements":7}}


def fixture():
    sensors={i:(1,i%4+1) for i in range(23)}
    row={"event":0,"generated":[{"id":PRIMARY,"eta":3.9,"pt":5.,"charge":1.,"truth":[0.,0.,0.,.04,.008,0.]}],
        "simulated_ids":[PRIMARY,SECONDARY],"simhits":23,"measurements":[
            {"index":i,"geometry_id":i,"particles":[PRIMARY] if i<9 else [SECONDARY] if i<16 else []} for i in range(23)],
        "spacepoints":[],"seeds":[{"measurements":[0,1,2,3]}],"estimated_seeds":[],"ckf":[],"ambi":[]}
    return row,sensors


def track(indices,index=0):
    return {"index":index,"measurements":indices,"nMeasurements":len(indices),"reference":True,
        "parameters":[0.,0.,0.,.04,.008,0.],"variance":[1.]*6,"chi2":1.,"ndf":8}


class MetricsTest(unittest.TestCase):
    def test_ambiguity_convergence_counts_track_sets_and_repeated_state_links(self):
        def states(indices):return {"states":[{"measurement":i,"inlier":True} for i in indices]+[{"measurement":99,"inlier":False}]}
        self.assertEqual(ambiguity_shared_max([]),0)
        self.assertEqual(ambiguity_shared_max([states([1,1,2])]),0)
        self.assertEqual(ambiguity_shared_max([states([1,1,2]),states([1,2,3])]),3)
        self.assertEqual(ambiguity_shared_max([states([1,2]),states([2,3])]),1)

    def test_all_events_and_secondary_fake_duplicate_are_distinct(self):
        row,sensors=fixture()
        row["ambi"]=[track(list(range(7)),0),track(list(range(1,8)),1),track(list(range(9,16)),2),track([0,1,9,10,16,17,18],3)]
        event=classify_event(row,sensors,CONFIG)
        self.assertEqual({k:event["ambi"][k] for k in ("accepted","matched","primary_candidates","secondary","fake","duplicates")},
                         {"accepted":4,"matched":1,"primary_candidates":2,"secondary":1,"fake":1,"duplicates":1})
        empty=copy.deepcopy(row);empty["event"]=1;empty["ambi"]=[]
        summary=summarize([event,classify_event(empty,sensors,CONFIG)],"ambi")
        self.assertEqual(summary["efficiency"]["value"],.5)
        self.assertEqual(event["ambi"]["representative"]["index"],0)
        self.assertTrue(event["pure_seed"])

    def test_completeness_and_invalid_covariance_are_enforced(self):
        row,sensors=fixture()
        for m in row["measurements"]:m["particles"]=[PRIMARY]
        row["ambi"]=[track(list(range(7)))]
        self.assertEqual(classify_event(row,sensors,CONFIG)["ambi"]["fake"],1)
        row["ambi"][0]["variance"][2]=None
        self.assertEqual(classify_event(row,sensors,CONFIG)["ambi"]["quality_rejected"],1)

    def test_unassociated_track_counted_as_fake(self):
        row,sensors=fixture();row["ambi"]=[track(list(range(16,23)))]
        self.assertEqual(classify_event(row,sensors,CONFIG)["ambi"]["fake"],1)

    def test_zero_fake_limit_includes_no_track_events(self):
        self.assertAlmostEqual(rate(0,5000)["zero_one_sided95_upper"],.000598966)
        self.assertIsNone(interval(0,0));self.assertEqual(rate(0,0)["value"],None)

    def test_configured_pixel_group_denominator_and_full_covariance(self):
        row,sensors=fixture();config=copy.deepcopy(CONFIG)
        config["matching"]["reconstructable_pixel_groups"]=9
        self.assertFalse(classify_event(row,sensors,config)["reconstructable"])
        row["ambi"]=[track(list(range(7)))];row["ambi"][0]["covariance_positive_definite"]=False
        self.assertEqual(classify_event(row,sensors,CONFIG)["ambi"]["quality_rejected"],1)

    def test_selection_refuses_heldout_input(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);case=root/"data/pt1/control";case.mkdir(parents=True)
            (case/"summary.json").write_text(json.dumps({"phase":"validation"}))
            config=root/"campaign.json";config.write_text(json.dumps({"profiles":{"control":{}},"pt_GeV":[1]}))
            with self.assertRaisesRegex(ValueError,"only consume tuning"):
                select(root/"data",root/"output",config)


if __name__=="__main__":unittest.main()
