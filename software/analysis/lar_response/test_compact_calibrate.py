"""Independent synthetic checks of fixed forward-gain cross-validation/refitting."""
import copy
import inspect
import json
import unittest

import numpy as np
import compact_calibrate as c


class HeldoutGainTests(unittest.TestCase):
    def geometry(self):
        return dict(compact_sha256='a'*64, materials_sha256='b'*64)

    def fixture(self, per_bin=10):
        eta = np.repeat((c.ETA_EDGES[:-1]+c.ETA_EDGES[1:])/2, per_bin)
        ids = np.arange(len(eta))
        energy = 10 + ids % 70
        folds = np.tile(np.arange(5), len(eta)//5)
        response = .15 + .03*folds
        return ids, eta, energy, energy*response, folds

    def contract(self):
        return dict(reference_compact_sha256='a'*64, candidate_compact_sha256='c'*64,
                    reference_materials_sha256='b'*64, candidate_materials_sha256='d'*64,
                    reference_primary_manifest_sha256='1'*64, candidate_primary_manifest_sha256='2'*64,
                    reference_primary_revision='3'*40, candidate_primary_revision='4'*40,
                    input_sha256='5'*64, truth_sha256='6'*64, transition_union_abs_eta=[1.2,1.6])

    def test_fold_assignment_is_stable_by_primary_identity(self):
        ids = np.arange(1000); a = c.make_folds(ids)
        shuffled = np.random.default_rng(13).permutation(ids)
        b = c.make_folds(shuffled)
        np.testing.assert_array_equal(a[shuffled], b)
        self.assertEqual(np.bincount(a).tolist(), [200]*5)
        with self.assertRaisesRegex(ValueError, 'unique'): c.make_folds([0,1,2,2,4])

    def test_forward_gain_and_signal_only_application_preserve_zero(self):
        ids,eta,energy,_,_ = self.fixture()
        model = c.fit_gain(np.full(len(ids), .2), eta, ids, self.geometry())
        np.testing.assert_allclose(model['gains'], .2)
        result = c.apply_calibration(model, [0.,4.,10.], [-.01,1.1,3.], self.geometry())
        np.testing.assert_allclose(result, [0.,20.,50.])
        self.assertEqual(list(inspect.signature(c.apply_calibration).parameters), ['model','signal_GeV','eta','geometry'])
        response = np.full(len(ids), .2); response[0] = 0
        fitted = c.fit_gain(response, eta, ids, self.geometry())
        self.assertAlmostEqual(fitted['gains'][0], .18)
        self.assertEqual(fitted['training_bin_multiplicities'][0], 10)

    def test_entire_heldout_fold_is_excluded_from_its_prediction(self):
        ids,eta,energy,signals,folds = self.fixture()
        prediction,models = c.out_of_fold(signals,energy,eta,ids,folds,self.geometry())
        altered = energy.copy(); altered[folds==0] *= 20
        changed,_ = c.out_of_fold(signals,altered,eta,ids,folds,self.geometry())
        np.testing.assert_array_equal(prediction[folds==0], changed[folds==0])
        self.assertTrue(np.any(prediction[folds!=0] != changed[folds!=0]))
        for i,model in enumerate(models):
            self.assertEqual(model['excluded_fold'],i)
            self.assertEqual(model['training_primary_ids_sha256'],c.ids_hash(ids[folds!=i]))
            self.assertEqual(model['heldout_primary_ids_sha256'],c.ids_hash(ids[folds==i]))
            self.assertEqual(model['training_multiplicity_total'],480)

    def test_multiplicities_refit_training_not_just_fixed_predictions(self):
        ids,eta,energy,signals,folds = self.fixture()
        plain,_ = c.out_of_fold(signals,energy,eta,ids,folds,self.geometry())
        weights = 1 + 4*(folds==0)
        refitted,models = c.out_of_fold(signals,energy,eta,ids,folds,self.geometry(),weights)
        selected=(eta < .05)&(folds!=2)
        manual=np.sum(weights[selected]*signals[selected]/energy[selected])/weights[selected].sum()
        self.assertAlmostEqual(models[2]['gains'][0],manual)
        self.assertTrue(np.any(plain[folds==2] != refitted[folds==2]))
        # Weighted held-out moments equal explicit multiplicity expansion.
        ratio=refitted/energy;categories=np.zeros(len(ids),dtype=int)
        mean,width=c.pair.common.binned_moments(ratio,categories,weights,1)
        expanded=np.repeat(ratio,weights)
        self.assertAlmostEqual(mean[0],expanded.mean())
        self.assertAlmostEqual(width[0],expanded.std(ddof=1)/expanded.mean())

    def test_invalid_training_and_model_scope_fail(self):
        ids,eta,energy,signals,_ = self.fixture()
        response=signals/energy
        with self.assertRaisesRegex(ValueError,'Missing training'):c.fit_gain(response[:-10],eta[:-10],ids[:-10],self.geometry())
        zero=response.copy();zero[:10]=0
        with self.assertRaisesRegex(ValueError,'Nonpositive'):c.fit_gain(zero,eta,ids,self.geometry())
        model=c.fit_gain(response,eta,ids,self.geometry())
        wrong=dict(self.geometry(),materials_sha256='f'*64)
        with self.assertRaisesRegex(ValueError,'scope mismatch'):c.apply_calibration(model,[1.],[.2],wrong)
        broken=copy.deepcopy(model);broken['gains'][0]=0
        with self.assertRaisesRegex(ValueError,'Invalid calibrated gains'):c.apply_calibration(broken,[1.],[.2],self.geometry())
        with self.assertRaisesRegex(ValueError,'outside declared bins'):c.apply_calibration(model,[1.],[3.1],self.geometry())

    def test_refit_bootstrap_models_and_no_heldout_recentering(self):
        ids,eta,energy,signals,_=self.fixture(per_bin=50)
        # Synthetic model pair shares predictions exactly; changes are provenance only.
        vals=np.column_stack([energy,eta,np.linspace(-3.1,3.1,len(ids)),signals,signals/energy])
        loaded={name:([{'event':int(i)} for i in ids],vals.copy(),{}) for name in c.MODELS}
        source=dict(analysis_sha256='7'*64,source_revision='8'*40)
        result,artifact=c.summarize(loaded,self.contract(),source,bootstrap=8)
        self.assertEqual(result['events'],len(ids))
        for name in c.MODELS:
            model=artifact['models'][name]
            self.assertEqual(len(model['fold_models']),5)
            self.assertEqual(model['full_fit_reuse_only']['kind'],'full-fit-reuse-only')
            self.assertIn('not evaluated on independent',model['full_fit_reuse_only']['validation_status'])
            self.assertEqual(result['models'][name]['global']['events'],len(ids))
            self.assertEqual(result['bootstrap']['requested_fold_refits_per_model'],40)
            self.assertEqual(result['bootstrap']['completed_fold_refits'][name],40)
            self.assertEqual(result['bootstrap']['complete_prediction_replicates'][name],8)
        contrast=result['candidate_minus_reference']['global'][0]
        self.assertAlmostEqual(contrast['difference'],0)
        np.testing.assert_allclose(contrast['ci95'],[0,0])
        # Deliberate fold-dependent forward response need not close at unity:
        # compare the emitted mean to direct held-out application, without recentering.
        folds=c.make_folds(ids)
        estimate,_=c.out_of_fold(signals,energy,eta,ids,folds,self.geometry())
        self.assertAlmostEqual(result['models']['reference']['global']['mean_response'],np.mean(estimate/energy))
        self.assertNotEqual(result['models']['reference']['global']['mean_response'],1.)
        hist=result['models']['reference']['global']['calibrated_response_histogram']
        self.assertEqual(sum(hist['counts'])+hist['underflow']+hist['overflow'],len(ids))
        self.assertEqual(hist['normalization'],'Ehat/Etrue, no normalization by fitted evaluation mean')
        json.dumps(result,allow_nan=False);json.dumps(artifact,allow_nan=False)

    def test_invalid_bootstrap_gain_is_reported_without_redraw_or_drop(self):
        ids,eta,energy,signals,_=self.fixture()
        folds=c.make_folds(ids);first=np.flatnonzero(eta<.05)
        # Two distinct-fold positive primaries keep every point training fit valid,
        # while their absence in some bootstrap draws makes the gain undefined.
        signals[first]=0
        selected=[first[0],next(i for i in first if folds[i]!=folds[first[0]])]
        signals[selected]=.2*energy[selected]
        vals=np.column_stack([energy,eta,np.linspace(-3.1,3.1,len(ids)),signals,signals/energy])
        loaded={name:([{'event':int(i)} for i in ids],vals.copy(),{}) for name in c.MODELS}
        result,_=c.summarize(loaded,self.contract(),{},bootstrap=20)
        self.assertEqual(result['bootstrap']['replicates'],20)
        for name in c.MODELS:
            invalid=result['bootstrap']['invalid_gain_replicates'][name]
            self.assertGreater(len(invalid),0)
            self.assertEqual(result['bootstrap']['complete_prediction_replicates'][name],20-len(invalid))
            interval=result['models'][name]['global']['fractional_width_bootstrap']
            self.assertIsNone(interval['ci95'])
            self.assertGreaterEqual(interval['undefined'],len(invalid))
        json.dumps(result,allow_nan=False)


if __name__=='__main__':unittest.main()
