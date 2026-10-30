"""Named particle hypotheses; gun, propagation and scoring share one identity."""

SPECIES = {"muon": (13, "eMuon"), "electron": (11, "eElectron"), "pion": (211, "ePionPlus")}


def configure(acts, name):
    if name not in SPECIES:
        raise ValueError("Unsupported benchmark species: " + str(name))
    pdg, enum_name = SPECIES[name]
    hypothesis = getattr(acts.ParticleHypothesis, name)
    if abs(int(hypothesis.absolutePdg)) != pdg:
        raise ValueError("Native hypothesis does not match gun species")
    return getattr(acts.PdgParticle, enum_name), hypothesis, {
        "name": name, "absolute_pdg": pdg, "mass_GeV": hypothesis.mass,
        "absolute_charge": hypothesis.absoluteCharge,
        "finder": "multicomponent-brem-CKF" if name == "electron" else "CKF",
    }


def audit_event(row, expected):
    """Verify actual native identities; ancestry never changes truth matching."""
    import math
    import numpy as np
    if len(row["generated"]) != 1:
        raise ValueError("Species benchmark requires one generated primary")
    primary = row["generated"][0]
    pdg = expected["absolute_pdg"]
    if abs(primary["pdg"]) != pdg or np.float32(primary["mass_GeV"]) != np.float32(expected["mass_GeV"]):
        raise ValueError("Generated species or mass differs from configured hypothesis")
    sign = 1 if primary["pdg"] > 0 else -1
    charge = sign if pdg == 211 else -sign
    if primary["charge"] != charge:
        raise ValueError("Generated PDG and charge disagree")
    if len(row["estimated_hypotheses"]) != len(row["estimated_seeds"]):
        raise ValueError("Estimated hypotheses and seeds differ in length")
    hypotheses = row["estimated_hypotheses"] + [t["hypothesis"] for stage in ("ckf", "ambi") for t in row[stage]]
    if any(h["absolute_pdg"] != pdg or np.float32(h["mass_GeV"]) != np.float32(expected["mass_GeV"]) for h in hypotheses):
        raise ValueError("Reconstruction used the wrong particle hypothesis")
    particles = row["simulated_particles"]
    identities = {tuple(p["id"]) for p in particles}
    if len(identities) != len(particles) or identities != {tuple(i) for i in row["simulated_ids"]}:
        raise ValueError("Detailed simulated identities disagree with native truth collection")
    original = [p for p in particles if p["id"] == primary["id"]]
    if original and (original[0]["pdg"] != primary["pdg"] or original[0]["charge"] != primary["charge"]):
        raise ValueError("Transport changed primary identity")
    ratio = (original[0]["p_final_GeV"] / original[0]["p_initial_GeV"]
             if original and original[0]["p_initial_GeV"] > 0 else math.nan)
    return ratio, [p["pdg"] for p in particles if p["id"] != primary["id"]]
