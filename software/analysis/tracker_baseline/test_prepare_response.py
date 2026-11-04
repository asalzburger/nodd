"""Selected response must preserve coordinate roles and reject wrong native IDs."""
import copy
import unittest
from prepare_response import prepare


class SelectedResponseTests(unittest.TestCase):
    def setUp(self):
        self.selection = dict(pitch_mm=[.075,2.],previous_pitch_mm=[.075,.5])
        self.sensors = [dict(geometry_id=(s<<56)|(2<<36)|(1<<8), ids=dict(system=s)) for s in range(1,8)]
        self.widths = dict(schema_version=1,status='PROTOTYPE',width_convention='synthetic fixture',groups=[
            dict(volume=s,index=i,sigma_mm=.1,mean_mm=0.,uncentered_rms_mm=.1,entries=10,
                 sensor_family='pixel' if s<4 else 'short_strip' if s<6 else 'long_strip')
            for s in range(1,8) for i in ([0,1] if s<6 else [0])])

    def test_only_strixel_second_coordinate_changes(self):
        original=copy.deepcopy(self.widths)
        scaled,digi,audit=prepare(self.sensors,self.widths,self.selection)
        self.assertEqual(self.widths,original)
        self.assertEqual(audit['scaled_strixel_volumes'],[4,5])
        for before,after in zip(original['groups'],scaled['groups']):
            expected=copy.deepcopy(before)
            if before['volume'] in (4,5) and before['index']==1:expected['sigma_mm']*=4
            self.assertEqual(after,expected)
        self.assertEqual(len(digi['entries']),7)

    def test_incomplete_or_wrong_native_identity_rejected(self):
        with self.assertRaises(ValueError):prepare(self.sensors[:-1],self.widths,self.selection)
        self.sensors[0]['geometry_id']=20<<56
        with self.assertRaises(ValueError):prepare(self.sensors,self.widths,self.selection)

    def test_other_selection_and_extra_widths_rejected(self):
        with self.assertRaises(ValueError):prepare(self.sensors,self.widths,dict(self.selection,pitch_mm=[.075,1.5]))
        self.widths['groups'].append(dict(self.widths['groups'][0],volume=99))
        with self.assertRaises(ValueError):prepare(self.sensors,self.widths,self.selection)
