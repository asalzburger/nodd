"""Publish compact binwise evidence; full event data/covariance stay local."""
import argparse
import hashlib
import json
from pathlib import Path


def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def publish(source,output):
    data=json.loads(source.read_text())
    # Correlations retained for the principal global / angular comparisons.
    # Other curves use their full paired pointwise intervals, not joint tests.
    selected={}
    for field in ('width_covariance','contrast_covariance'):
        cov=data.get(field)
        if not cov or not isinstance(cov,dict) or 'order' not in cov:continue
        indices=[i for i,key in enumerate(cov['order']) if key.split(':')[-2] in ('global','abs_eta','siw_folded_phi')]
        selected[field]=dict(original_variables=len(cov['order']),published_variables=len(indices),axes=['global','abs_eta','siw_folded_phi'])
        cov['order']=[cov['order'][i] for i in indices]
        cov['matrix']=[[cov['matrix'][i][j] for j in indices] for i in indices]
    def portable(value):
        if isinstance(value,str):return value.replace(str(Path.home()),'$USER_HOME')
        if isinstance(value,list):return [portable(v) for v in value]
        if isinstance(value,dict):return {portable(k):portable(v) for k,v in value.items()}
        return value
    data=portable(data)
    data['publication']=dict(full_private_summary_sha256=sha(source),publisher_sha256=sha(Path(__file__)),
        covariance_selection=selected,numeric_statistics='All per-bin statistics, paired intervals, histograms and counts retained unchanged; principal covariance is an exact submatrix.',
        paths='User-home runtime paths normalized to $USER_HOME; raw receipt/library/source hashes retained.')
    output.parent.mkdir(parents=True,exist_ok=True);output.write_text(json.dumps(data,indent=2,allow_nan=False)+'\n')
    if '/Users/' in output.read_text():raise ValueError('Unnormalized private path')
    print(output,output.stat().st_size,'bytes')


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--summary',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();publish(a.summary,a.output)
