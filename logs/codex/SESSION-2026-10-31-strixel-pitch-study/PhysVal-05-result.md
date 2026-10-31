# PhysVal-05 — high-pT digital-response diagnostic

Read-only source c2453e91255c023f724028f2eb5f1b0f365106c3; native inventory
SHA256 b8709852ba103e36a68e21f8de0df61b4b02ab30b2c3ebbddf1402259f4d18bf.
All twelve native report/full-array hash bindings passed. No source changes.

At100GeV, |eta|<1 has5036identical successful/native-matched/valid-covariance
events per pitch. Measurement counts agree. z0width68 is4.0207/3.5565/3.2949/
3.0932um for0.5/1/1.5/2mm; uncut SD5.2144/5.1047/5.0285/4.8978um.
Pull SD0.5429/0.4918/0.4737/0.4576; median predicted uncertainty increases
8.713/9.145/9.249/9.281um. Theta behaves similarly, with strongest symmetric
effect at|eta|~0.25–0.75. Bias remains small. This is not attrition.

Exact full100GeV digitization configurations become identical after restoring
only the12384strixel local-v grids: no coordinate-swap/isolation defect found.
The existing small1GeV measurement-writing pilot has central pixel local-v
normalized residual SD0.447 versus baseline strixel1.011; pixel response stays
identical, while coarser strixel hit RMS worsens118→260→393→538um. This supports
a covariance/response-weighting interpretation but does not prove the entire
high-pT mechanism. The reviewer recommends a separate four-pitch5000-event
100GeV Gaussian p/sqrt(12), noMerge control, with all measured axes consistent.
No tuning to suppress the observed effect. A calibrated physical response is
still required to choose a baseline; no physical benefit or design approval
is established by the narrower native digital core.
