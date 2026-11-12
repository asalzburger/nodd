"""Aggregate primary-distribution checks; no detector responses are inspected."""
import argparse
import json
from pathlib import Path
import numpy as np
from angular_sample import save, sha
from angular_analyze import ETA_EDGES, PHI_EDGES, folded_phi


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--campaign',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    manifest=json.loads((a.campaign/'campaign.json').read_text());result={}
    for split in ('train','validation'):
        records=[]
        for entry in manifest['batches']:
            if entry['split']!=split:continue
            path=a.campaign/entry['input']/'truth-input.jsonl'
            if sha(path)!=entry['truth_sha256']:raise ValueError('Changed primary ledger')
            records.extend(json.loads(line) for line in path.read_text().splitlines())
        energy=np.array([r['energy_GeV'] for r in records]);eta=np.array([r['eta'] for r in records]);phi=np.array([r['phi'] for r in records])
        histogram,edges=np.histogramdd(np.column_stack([energy,abs(eta),folded_phi(phi)]),
                                      bins=[np.linspace(10,80,15),ETA_EDGES,PHI_EDGES])
        if histogram.sum()!=len(records):raise ValueError('Primary outside declared distributions')
        result[split]=dict(events=len(records),energy_mean_GeV=float(energy.mean()),eta_mean=float(eta.mean()),
            phi_mean_rad=float(phi.mean()),E_eta_phi_correlation=np.corrcoef([energy,eta,phi]).tolist(),
            energy_bin_edges_GeV=edges[0].tolist(),abs_eta_edges=edges[1].tolist(),folded_phi_edges_rad=edges[2].tolist(),
            joint_bin_counts=histogram.astype(int).tolist(),normalization='Electrons per bin; counts sum to split total; no response selection',
            joint_occupancy=dict(minimum=int(histogram.min()),maximum=int(histogram.max()),mean=float(histogram.mean()),
                                 empty_bins=int((histogram==0).sum())))
    a.output.parent.mkdir(parents=True,exist_ok=True)
    save(a.output,dict(status='PROTOTYPE input-only audit; validation response performance uninspected',
        campaign_sha256=sha(a.campaign/'campaign.json'),producer_sha256=sha(__file__),splits=result))


if __name__=='__main__':main()
