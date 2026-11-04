# TTBAR-PU200-SoftEng-07 — actual compiler failure diagnosis

Exact project base250a211 plus four dirty diagnostic sources, actual ACTS355ea. All100 baseline pixel-input events match preserved original ordered seed IDs and quality bits across shared Core, renamed and instrumented copies. Wall192.35s; native totals30.96/32.50/33.23s. Only event57 raises one FLTDIV per implementation.

Actual shared Core divides at0x23a714 before selecting at0x23a71c. Instrumented capture-v2 divides at0x69514 before selecting at0x6951c; recorded relative fault offsets match. Event57 update1,369,234 has barrel n2 logical index2/physical103, n1 index1/physical102, equal z169.1857452392578mm, slope bits0x80000000 (-0), squared slope bits0 (+0), curvature0. Source-unselected endcap division is evaluated speculatively.

All4,889seed IDs/quality bits remain identical in event57. Unique original points14988/18624 match all xyz bits; no outputseedcontainsboth, which is membership evidence rather than final-chain ancestry proof. No guard, full reconstruction or commit performed. All native diagnostic jobs stopped before handoff. Original source/generated/module/cache/ninja/hash manifest preserved locally; four original sourcefiles and exactdriver now retained in this sessionfolder. Canonical sanitized reports/state and raw-input hashes are in DES042/ttbar-pu200/gbts-numerical-diagnosis.json. Original moduleba7724cfda0e6406962b6aeca40a3b2c54e707b4521ed2cdf14587b3fd505185; capture-v2 module52efb2f8e66a05979af53029526d420f12ba456a70a4e1eac669fd1d77f328fd.

Recommended minimal rewrite selects denominator first, then divides, with no rejection or cut change. Native/strict ±0/boundary controls, actualsafeassembly, all100seed comparisons and complete production executeaudit remain required.
