# Prepared draft pull request

Publication status: no PR created. Automatic approval review rejected the
creation action because the GitHub destination/publication had not been explicitly
authorized. Branch codex/strixel-pitch-truth-study was already pushed ataa9b0e7;
no subsequent remote update or alternate publication action was attempted.
The following title/body is ready for user authorization.

## Title

Tracker: study longitudinal strixel pitch, power and service space

## Description

Adds an isolated DES-042 study of0.5/1/1.5/2mm strixel local-v pitch on the
current balanced tracker, with fixed75µm fine pitch, geometry, material and3T.
The detector baseline remains unchanged.

- Retains12×20000native geometric Fatras/truth-Kalman case-events atpT1/10/100GeV,
  plus4×5000separate100GeV Gaussian pitch/√12 controls. Failed events, native
  matching, uncut residuals/pulls and paired-bootstrap uncertainties are retained.
- Gaussian central100GeV z0widths worsen10.6±1.9 /11.7±2.2 /13.2±2.4%, theta
  15.9±2.3 /21.6±2.8 /22.9±3.1%. Apparent native geometric improvement is
  documented with pull nonclosure and a verified covariance coupling. Both
  response hypotheses remain visible; neither is calibrated physical performance.
- Channels reduce50/66.7/75%. Existing proxy loads with all electronics channel
  dependent yield49–201 /65–268 /73–301kW heat reduction. Conditional unqualified
  harness redesign removes243/273/273L gross envelope; unchanged hardware saves
  zero installed space. Fibres, cooling and trays remain fixed.
- Provides explicit-build native launchers, portable all-event data, deterministic
  analysis/report replay,26unrooted/Matplotlib PNG/PDF figures and CI checks.

Validation:22tests; all260000processed case-events completed; exact truth/hit
pairing, physical-input invariance and517888Gaussian variance checks. Full
deterministic uncertainty replays pass. Separate final PhysVal ataa9b0e7 and
independent SysArch arithmetic have no remaining material findings within scope.
Exact source/binary identities, limitations and unavailable token counters are
retained in the paired session journal.

Results: docs/validation/DES-042/results.md. Reproduction:
software/analysis/strixel_pitch_study/README.md. DES-042 remainsDRAFT/PROTOTYPE.
