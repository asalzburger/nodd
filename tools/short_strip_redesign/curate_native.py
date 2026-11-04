#!/usr/bin/env python3
"""Retain aggregate native construction evidence, never XML/ROOT entity dumps."""
import argparse
import json
from pathlib import Path
from model import sha


def curate(source):
    raw=json.loads(source.read_text())
    contacts=raw['thermal_contact_screen'];coverage=raw['source_coverage']
    out={key:raw[key] for key in ('status','errors','engineering_status','scope','counts','solid_count','composite_count','window_probes','identifiers','disc_layers','probe_counts','overlap_tolerance_mm','guard_clearance','capacity_policy','provenance','limitations')}
    out['raw_native_report_sha256']=sha(source)
    out['overlap_count']=len(raw['overlaps'])
    out['source_coverage']=dict(total_rays=coverage['total_rays'],checks=len(coverage['checks']),target_annulus_mm=coverage['target_annulus_mm'],failed_rays=sum(x['failed_rays'] for x in coverage['checks']),minimum_outer_margin_mm=min(x['minimum_outer_margin_mm'] for x in coverage['checks']))
    out['pipe_contact_screen']=dict(checked_modules=len(contacts['rows']),definite_missing_contacts=contacts['definite_missing_contacts'],scope=contacts['scope'])
    out['curator_sha256']=sha(__file__)
    return out


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--input',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    result=curate(a.input)
    if result['status']!='PASS' or result['overlap_count'] or result['pipe_contact_screen']['definite_missing_contacts']:raise ValueError('Native construction failed; retain adverse evidence separately')
    a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(result,indent=2,allow_nan=False)+'\n')
    print(f"Retained aggregate native evidence: {result['counts']['sensitive']} sensors, zero overlaps")


if __name__=='__main__':main()
