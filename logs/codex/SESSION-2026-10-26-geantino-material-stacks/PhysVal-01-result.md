# GEANTINO-PhysVal-01 — bounded separate assessment

Reviewed 4008abf1c4c76bbfd5f7df64dcfd81ee5e62e768 under the explicit generic-agent
PhysVal mandate. No repository edits, native simulation, installs, environment
activation, external access or further delegation.

P2: original workspace provenance did not identify packaged classifier/launcher
hashes. Resolved by the supplemental 4008abf native rerun, retained separately in
native-rerun-4008abf.json (SHA256 7a884c9ec38eb36a7c331410dd4045993f20732ba89facb7a53fdc4d30a30560).
The reviewer independently checked its actual ROOT output against pinned inputs.

P3: symmetric half-max float spacing exceeds the actual cell at powers of two.
At float32 128 the lower bound was 127.9999923706 instead of 127.9999961853.
None of the six retained corrections hits this case. Fix with asymmetric bounds;
separate correction assessment follows.

Normalization including zero contributions and covariance-aware total errors are
sound for the retained scan. DD4hep sensitivity flags are used, conditional on the
reconstructed geometry. The pre-step implementation is consistent, but the
unknown original recording writer version was not independently established.
Finite-grid rescues do not bound all continuous positions or geometry identity.
The full budgets of two identified ambiguous contributions are retained as bounds.

Actual checks: pinned source reads; finite/nonnegative profile arrays, ordered
edges, common counts and weighted/additive means; all axes contain 100000 tracks
with minimum occupancy 1036/2124/1300; six CSVs match compact data. All 54 native
profiles exactly match pinned edges, counts, means and variances. Independent
per-track means/population SEM and all six precision bounds pass. Closure maxima
are 5.77047e-6 X0 and 1.22651e-6 interaction lengths. Ambiguous entries 47872 and
86513 give maximum eta-bin shifts 1.45946e-10 X0 and 2.99372e-11 interaction lengths.
All 12 retained figures at the pinned revision matched original artifact hashes;
later SVG whitespace normalization is a distinct packaging change.

No blocking issue remains for the narrowly stated scan reduction after retaining
the native provenance correction. Original seed/command/geometry revision remain
unknown. Density agreement does not establish same-density recipes or boundaries.
Technical assessment only; no detector acceptance or human sign-off.
