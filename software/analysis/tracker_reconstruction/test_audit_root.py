"""A missing campaign must never produce a successful persistence audit."""
from pathlib import Path
import json
import tempfile
import unittest
import awkward as ak
import numpy as np
import uproot
from audit_root import audit, contains_perigee_tuple, PARAMETERS


class PersistenceControls(unittest.TestCase):
    def test_empty_or_broken_staging_is_rejected_without_a_pass_artifact(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);output=root/"audit.json"
            with self.assertRaisesRegex(ValueError,"No native ROOT cases"):
                audit(root/"missing",root/"analysis",output)
            self.assertFalse(output.exists())

    def fixture(self,root,event_ids=(0,1),volume=1,variance=4.):
        """Two zero-track events make missing-event coverage observable."""
        native=root/"native";analysis=root/"analysis";relative=Path("electron/pt1")
        case=native/relative;reduced=analysis/relative
        case.mkdir(parents=True);reduced.mkdir(parents=True)
        (case/"run-report.json").write_text(json.dumps({"outcome":"completed"}))
        (case/"error-table.json").write_text(json.dumps({"groups":[
            {"volume":1,"index":0,"sigma_mm":2.},
            {"volume":1,"index":1,"sigma_mm":3.}]}))
        (reduced/"summary.json").write_text(json.dumps({"events":2,
            "stage_counts":{"measurements":1},"stages":{
                s:{"counts":{"raw":0}} for s in ("ckf","ambi")}}))
        np.savez(reduced/"events.npz",event=np.array([0,1]),
            ckf_matched=np.zeros(2),ambi_matched=np.zeros(2))
        with uproot.recreate(case/"measurements.root") as f:
            f.mktree("measurements",{"volume_id":"uint32","var_loc0":"float32",
                "var_loc1":"float32","clus_size":"uint32"}).extend({
                "volume_id":np.array([volume],dtype=np.uint32),
                "var_loc0":np.array([variance],dtype=np.float32),
                "var_loc1":np.array([9.],dtype=np.float32),
                "clus_size":np.zeros(1,dtype=np.uint32)})
        for stage in ("ckf","ambi"):
            fields={"track_nr":"var * int32",**{
                prefix+name+"_fit":"var * float32" for prefix in ("e","err_e")
                for name in ("LOC0","LOC1","PHI","THETA","QOP","T")}}
            values={name:ak.unflatten(np.array([],dtype=np.int32 if name=="track_nr" else np.float32),[0,0]) for name in fields}
            with uproot.recreate(case/("tracksummary_"+stage+".root")) as f:
                f.mktree("tracksummary",{"event_nr":"uint32",**fields}).extend({
                    "event_nr":np.array(event_ids,dtype=np.uint32),**values})
        return native,analysis,root/"audit.json"

    def test_zero_track_events_and_all_response_coordinates_are_audited(self):
        with tempfile.TemporaryDirectory() as directory:
            native,analysis,output=self.fixture(Path(directory))
            audit(native,analysis,output)
            case=json.loads(output.read_text())["cases"]["electron/pt1"]
            self.assertEqual(case["checked_variance_marginals"],2)
            self.assertTrue(case["stages"]["ambi"]["exact_event_ids_match"])

    def test_duplicate_zero_track_event_id_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            native,analysis,output=self.fixture(Path(directory),event_ids=(0,0))
            with self.assertRaisesRegex(ValueError,"ROOT event IDs"):
                audit(native,analysis,output)
            self.assertFalse(output.exists())

    def test_unknown_measurement_volume_cannot_escape_variance_audit(self):
        with tempfile.TemporaryDirectory() as directory:
            native,analysis,output=self.fixture(Path(directory),volume=999,variance=99.)
            with self.assertRaisesRegex(ValueError,"Unknown persisted measurement volume"):
                audit(native,analysis,output)
            self.assertFalse(output.exists())

    def test_perigee_and_uncertainty_must_match_same_complete_candidate(self):
        target=np.arange(6,dtype=np.float32);sigma=np.ones(6,dtype=np.float32)
        values=np.array([target,target+1]);errors=np.array([sigma+1,sigma])
        tree=ak.Array({**{"e"+name+"_fit":[values[:,i]] for i,name in enumerate(PARAMETERS)},
            **{"err_e"+name+"_fit":[errors[:,i]] for i,name in enumerate(PARAMETERS)}})
        self.assertFalse(contains_perigee_tuple(tree,0,target,sigma))
        # The complete second candidate matches; its position is irrelevant.
        self.assertTrue(contains_perigee_tuple(tree,0,target+1,sigma))
        errors[1,5]+=1
        changed=ak.Array({**{"e"+name+"_fit":[values[:,i]] for i,name in enumerate(PARAMETERS)},
            **{"err_e"+name+"_fit":[errors[:,i]] for i,name in enumerate(PARAMETERS)}})
        self.assertFalse(contains_perigee_tuple(changed,0,target+1,sigma))
