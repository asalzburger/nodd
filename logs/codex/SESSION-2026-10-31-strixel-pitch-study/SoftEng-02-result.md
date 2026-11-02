# SoftEng-02 — response source/feasibility assessment

Read-only c2453e91255c023f724028f2eb5f1b0f365106c3. No source changed
in this assignment. ACTS source355ea684 ModuleClusters.cpp lines26–38
breaks a geometric cluster into cells; lines249–258 use path/activation weights;
lines291–325 recompute both centroid coordinates and variances
V_i=(pitch_i²/12)sum(w²)/(sum w)². Initial digital/component-digital handling
in DigitizationAlgorithm.cpp397–455 is superseded by the merge stage.

Actual277-barrel-strixel-hit pilot check: fine-u positions are bitwise identical
across pitches, while mean fine-u variance rises0.0003143513→0.0003418697→
0.0003503972→0.0003544470mm² (12.8%). This is a concrete covariance coupling,
not proof of the entire100GeV core-width mechanism. A separate all-axis
Gaussian p/sqrt(12), noMerge control is feasible through new files composing
frozen preparation/reduction and existing native smearing scheduling.
Estimated3–5minute native effort for four5000-event cases plus control setup;
no shared source/dependency modification required. Implementation subsequently
authorized under distinct SoftEng03 and pinned58f49b9 before any native launch.
