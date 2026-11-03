# DES043-PhysVal-03 — initial design assessment

- Reviewed revision:895b9e1d6f5d7d365272cd273a2ba55a64d99d75.
- Independent generic agent with explicit PhysVal mandate; read-only.
- Outcome: one blocking physical premise, subsequently addressed by redesign.
- No native/future-code review or human acceptance claimed.

P1: old6..24degree pipes miss both6x60mm lands for three of33 modules in the
first petal. Independent0.5mm source sampling, subtracting0.5mm sampling allowance
and1.25mm tube radius, finds positive surface clearance lower bounds2.0688mm
(ring2,phi2.142857deg),10.8740mm(ring3,1.875deg),19.8544mm(ring4,1.666667deg).
The old assumed0.615701K/W thermal path is absent there. It cannot establish a
viable module even though the arithmetic and replay pass.

P3: stale1.7mm versus3.1mm insert scope; insert mass168.22 versus168.239485kg;
−20.664 versus−20.659875C; adverse/stress upperheat301.70/478.99 versus
301.693630/478.966266kW. Coordinator corrects scope/numbers, then supersedes
those values with the new physical saddle rather than retaining stale results.

Actual checks: all10portabletests and summary/eightfigure fingerprint replay
PASS at the old revision; nine assigned bytes match. Independent2880phi check:
51840rays, zero holes,0.609402mm minimum outer margin beyond703mm. Power/voltage/
thermal arithmetic matches; all576barrel-half taps checked, adverse return
0.185707V; independent worstpacking0.9618437335. Scopedmass−308.386293kg,
noinsulationcredit−135.196698kg at this OLD design.

The reviewer explicitly distinguishes finitecorner704.908682mm from sampled
703mm target, old/newgap114.757904/82.334813mm, and74.1279%net channel reduction
with added sensors. Electronics assumptions are not measured savings. Adverse
flow6.048kg/s exceeds5.040kg/s comparator. Material is scoped and depends on
legacy composition; Cu-onlyη excludes other detector material. Previous2mm
reconstruction cannot validate changed physical geometry.

Remediation direction (coordinator, not reviewed in this result): central saddle,
3..27degree stadium routing, actual finite native contacts/windows/overlaps,
recalculated thermal/material output. Later fixed-revision assessment required.
