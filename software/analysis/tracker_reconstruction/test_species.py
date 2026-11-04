"""Species identity, charge-sign and native-hypothesis observation controls."""
import copy
import unittest
import species


def fixture(pdg, charge):
    # Explicit synthetic mass fixture, not a detector or particle-table value.
    primary={"id":[1,0,0,1,0],"pdg":pdg,"charge":charge,"mass_GeV":1.25}
    simulated={**primary,"p_initial_GeV":10.,"p_final_GeV":3.}
    expected={"absolute_pdg":abs(pdg),"mass_GeV":1.25}
    row={"generated":[primary],"simulated_particles":[simulated],"simulated_ids":[primary["id"]],
         "estimated_hypotheses":[expected.copy()],"estimated_seeds":[{}],"ckf":[],"ambi":[]}
    return row,expected


class SpeciesControls(unittest.TestCase):
    def test_lepton_and_pion_charge_signs_both_polarities(self):
        for pdg,charge in ((11,-1),(-11,1),(13,-1),(-13,1),(211,1),(-211,-1)):
            row,expected=fixture(pdg,charge)
            self.assertEqual(species.audit_event(row,expected),(.3,[]))
            row["generated"][0]["charge"]*=-1
            with self.assertRaisesRegex(ValueError,"PDG and charge"):species.audit_event(row,expected)

    def test_wrong_generated_mass_or_species_fails(self):
        for key,value in (("pdg",13),("mass_GeV",2.)):
            row,expected=fixture(11,-1);row["generated"][0][key]=value
            with self.assertRaisesRegex(ValueError,"Generated species or mass"):species.audit_event(row,expected)

    def test_every_completed_track_and_estimated_hypothesis_is_checked(self):
        for stage in ("ckf","ambi"):
            row,expected=fixture(11,-1);row[stage]=[{"hypothesis":{"absolute_pdg":13,"mass_GeV":1.25}}]
            with self.assertRaisesRegex(ValueError,"wrong particle hypothesis"):species.audit_event(row,expected)
        row,expected=fixture(11,-1);row["estimated_hypotheses"]=[{"absolute_pdg":13,"mass_GeV":1.25}]
        with self.assertRaisesRegex(ValueError,"wrong particle hypothesis"):species.audit_event(row,expected)

    def test_same_species_daughter_remains_distinct(self):
        row,expected=fixture(211,1);daughter=copy.deepcopy(row["simulated_particles"][0]);daughter["id"]=[1,0,0,2,1]
        row["simulated_particles"].append(daughter);row["simulated_ids"].append(daughter["id"])
        self.assertEqual(species.audit_event(row,expected),(.3,[211]))

    def test_duplicate_native_id_and_missing_seed_hypothesis_fail(self):
        row,expected=fixture(11,-1);row["simulated_particles"]*=2
        with self.assertRaisesRegex(ValueError,"identities disagree"):species.audit_event(row,expected)
        row,expected=fixture(11,-1);row["estimated_hypotheses"]=[]
        with self.assertRaisesRegex(ValueError,"differ in length"):species.audit_event(row,expected)


if __name__=="__main__":unittest.main()
