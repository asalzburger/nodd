#!/usr/bin/env python3
"""Audit persisted primary truth after template refactoring; retain both banks."""
import argparse
from collections import Counter
import hashlib
import json
import math
from pathlib import Path


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def inspect(path, events):
    import ROOT
    import DDG4  # Load dictionaries for Geant4Particle.
    f = ROOT.TFile.Open(str(path))
    if not f or f.IsZombie():
        raise RuntimeError('Unreadable ROOT output')
    tree = f.Get('EVENT')
    if not tree or tree.GetEntries() != events:
        raise RuntimeError('Wrong persisted event count')
    branches = [str(b.GetName()) for b in tree.GetListOfBranches()]
    if branches != ['MCParticles']:
        raise RuntimeError('Expected MC truth without fabricated hit branches')
    primary_bank, multiplicity, momenta = [], [], []
    for entry in tree:
        particles = entry.MCParticles
        primaries = [p for p in particles if len(p.parents) == 0]
        if len(primaries) != 1:
            raise RuntimeError('Expected exactly one parentless primary')
        p = primaries[0]
        momentum = math.sqrt(p.psx**2 + p.psy**2 + p.psz**2)
        if int(p.pdgID) != 22 or p.mass != 0 or abs(momentum - 20000) > 1e-6:
            raise RuntimeError('Primary does not match requested20GeV gamma')
        if any(x != 0 for x in (p.vsx, p.vsy, p.vsz)):
            raise RuntimeError('Unexpected primary vertex')
        primary_bank.append([float(x) for x in (p.psx, p.psy, p.psz)])
        multiplicity.append(len(particles))
        momenta.append(momentum)
    f.Close()
    return dict(sha256=digest(path), size_bytes=path.stat().st_size, events=events,
                branches=branches, primary_pdg=22, one_parentless_primary_per_event=True,
                primary_momentum_range_MeV=[min(momenta), max(momenta)],
                particle_multiplicity_histogram=dict(sorted(Counter(multiplicity).items())),
                primary_bank_sha256=hashlib.sha256(json.dumps(primary_bank).encode()).hexdigest(),
                primary_bank=primary_bank, multiplicities=multiplicity)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--before', type=Path, required=True)
    parser.add_argument('--after', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--events', type=int, default=1000)
    args = parser.parse_args()
    before, after = inspect(args.before, args.events), inspect(args.after, args.events)
    expected_before = '098ea5e0766a31295ee9a945a510e9d84b9cce3d9a58bc687c1c1845bb18e5f9'
    if before['sha256'] != expected_before:
        raise RuntimeError('Baseline ROOT differs from retained committed-source evidence')
    report = dict(status='PASS', before=before, after=after,
                  equal_primary_banks=before.pop('primary_bank') == after.pop('primary_bank'),
                  equal_particle_multiplicities=before.pop('multiplicities') == after.pop('multiplicities'),
                  script_sha256=digest(Path(__file__)),
                  scope='Air envelope transport and primary-truth audit only; no chamber response or solid-angle efficiency.')
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report))


if __name__ == '__main__':
    main()
