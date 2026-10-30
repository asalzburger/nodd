# RECO-SPECIES-SoftEng-02 — plotting and report generators

Input9f30a4fdb25f81a6edd16288ca46277293fb4961. Authored only plot.py,
species_plot.py andspecies_report.py. Existing muon plotting defaults preserved;
new per-case labels/references and full five-population efficiency comparison.
Full six-parameter pT pull overlays and all seven plot pairs per added case;
report retains rates, central widths/bias/tails, charge/secondary/matching,
primary outcomes and per-eta KilledTime diagnostics.

Actual checks with analysisPython3.11.15: syntax/CLI help; all seven default
muon PNGs and pull-tailJSON byte-identical to pinned producer; all four original
muon reductions reproduce efficiencies, coverage, central widths and q/p tails.
In-memory outcome/time/missing/tail boundary controls and direct-directory
keyword replay pass. Pull layout visually inspected. No fake matrix outputs,
native jobs, commits or dependency changes. Main integrates real evidence.
