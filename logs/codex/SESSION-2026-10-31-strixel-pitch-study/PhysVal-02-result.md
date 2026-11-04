# PhysVal-02 — source assessment

Examinedf8967e9b6f86b807b088d187cf2acc6e50e63ce1, read-only. Independently ran
exact pinned truth/test source in memory:4tests PASS. No native run or final
statistics assessment in this assignment.

P2: truth.py reused fitted-minus-truth arrays but advertised truth-minus-fitted.
Widths unaffected, bias/pull metadata wrong. Corrected before production in
8b7c147b3b0da4bd40dcd9ad06c98abcb2de58f9 with synthetic sign regression.
Source controls otherwise cover balanced compact/counts, geometry/map semantic
comparison, actual geometric segmentation, unique primary fit guard, all-event
arrays, generated/physical-hit payload hashes and single-cell diagnostics.
Fingerprint imported metrics.py separately; later exact full-array replay and
launch/completion byte checks explicitly supplement the omitted preparation
entry. Multi-cell covariance must be described as native pitch-derived clustered
covariance, with p²/12 only in the single-cell limit. Final bootstrap/result
review remains separate.
