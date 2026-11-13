# First matched LAr / Si–W 10k raw-response comparison

Status: **PROTOTYPE**. User-authorized on 2026-11-13, before LAr shower
results were inspected. Governing geometry: DES032/DES033; unchanged LAYOUT002
ECAL, including cryostat and local-service material. This study supplies no
engineering acceptance, digitized-response qualification or technology selection.

Resumed after merged PR139 (`f68cef1f949d941fc7f67c74357ab99059be0345`).
The maintained LAr export now uses reusable solid period mothers, preserving
physical leaves, materials and readout. The comparison therefore measures this
updated simulation hierarchy; numerical navigation boundaries can affect shower
histories. The failed legacy-hierarchy pilot is retained as diagnostic evidence,
not included in the response sample. Serial preinitialization and serial/MT
controls must pass before the twelve-worker production run.

## Prospective scope

**NODD DESIGN CHOICE:** reuse exactly the 10,000 original Si–W primary records:
single origin electrons, independently uniform total E=10–80 GeV, eta −3…3,
phi −pi…pi. HEPEvt SHA256:
`44bf93acf342ccfd9f461423ea12992ab1cab9046f84841ff8853ed763aad389`;
truth-ledger SHA256:
`b53199a644e659eb6efdd4684b824c6b85f66e0968686b0af3482e93b56c30b1`.
Use the retained original and physically staggered Si–W raw responses as
comparators. The staggered 10k transport precedes PR137's larger independent
calibration sample; its 10k raw population must not be labelled as PR137's 20k.

Construct the complete selected ECAL only, B=0, omitting tracker/beam pipe,
solenoid, HCAL and FCAL, consistently with the saved Si–W benchmark. Preserve
the LAr package's native geometry, material, segmentation and local services.
Use existing Geant4 11.4.3 / DD4hep 1.38 / ROOT 6.40.04, FTFP_BERT, 0.7 mm
production range cut, event seeds and twelve workers. Record actual installed
versions, library/source/configuration hashes and per-worker policy.

**NODD DESIGN CHOICE — numerical transport:** apply a declared maximum charged
step of 5 mm to active LAr, matching the saved Si–W numerical cap. Preserve
any existing tighter native limit and report native/applied limits separately.
No charge quenching, noise, digitization or reconstruction is introduced.
Record actual material composition/density, Birks constant, StepLimiter
processes, region cuts, field and active-volume inventory. Run a 100-primary
native-limit versus 5 mm pilot before production; this is a gross sensitivity
diagnostic, not statistical convergence or grounds to choose the nicer response.
Keep the predeclared 5 mm production policy irrespective of pilot mean differences.

## Observables and inference

Primary per-event observable: `R = sum(active ECAL deposited energy) / primary
total energy`. Retain every generated event, including empty collections/zero
signal. Report raw mean, sample SD, SD/mean, quantiles, zeros and the diagnostic
tail `R < 0.5 * sample mean(R)`. The latter is normalized to each technology's
own sample mean and is not a calibrated energy threshold or prediction.
Different mean sampling fractions are expected and do not rank performance.

Report inclusive and ten equal |eta| bins over 0…3; fourteen 5 GeV primary
energy slices over 10…80 GeV; sixteen equal full-phi bins; twelve signed-eta
bins. Also report ten bins of phi folded with the Si–W 22.5 degree sector
period, explicitly labelled as a **Si–W seam coordinate applied to both
models**. It is not the LAr electrode period. Absolute phi/signed eta controls
must accompany it. Show underlying response distributions and directional
mean/width/tail controls rather than a resolution curve alone.
Retain additional broad |eta| regions [0,1.2), [1.2,1.5), [1.5,3], with
3,999 / 999 / 5,002 common primaries, to expose the known partial-depth
barrel/endcap transition without removing it from the inclusive result.

Use 1,000 shared whole-primary-event bootstrap replicates (fixed analysis seed
13001000) for pointwise 95% percentile intervals and paired differences of
widths. A paired index preserves common primary illumination; showers in
different geometries are distinct stochastic histories, even with equal event
seeds. The bootstrap conditions on the saved transport/configurations and does
not estimate geometry, physics-list, material or electronics systematics.
Preserve cross-technology/angular width covariance for the principal global,
|eta| and folded-phi observables. Intervals are pointwise, not simultaneous.

These widths mix the energy spectrum, angular nonuniformity, dead material,
leakage and non-Gaussian tails. They are not fixed-energy intrinsic energy
resolution. No calibration is fitted in this first raw comparison. A future
calibrated comparison needs separately frozen technology-specific training
and fresh validation primaries.

## Integrity and retained evidence

Verify complete unique primary IDs independent of ROOT output order; saved
primary momenta/energies/directions against exact inputs; expected hit collection
names; raw/canonical identifiers, positive finite deposits and worker event
totals. Bind event ledgers to successful transport receipts and readback hashes.
Keep full ROOT/event ledgers/logs ignored locally. Commit only code, prospective
protocol, reproduction instructions, compact statistics/covariance and PNG/PDF/SVG
figures. Do not alter existing evidence or delete retained samples for disk space.

The known LAr electrode-material approximation and conservative support/cryostat
proxies remain. Barrel/endcap transition, wheel supports and differing outer
envelopes contribute to the measured candidate comparison. Results do not isolate
the active-medium technology or establish pp pileup/radiation suitability.
