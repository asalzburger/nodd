# SESSION-2026-09-15-cms-mtd-download — Acquire CMS MTD TDR

## Scope and evidence

M0 source acquisition on `adr-004`. Starting revision and pre-existing changes
are recorded in the paired JSON. Existing staged work, source instructions and
prior acquisition receipts were preserved. No commit or push was performed.

## Selected conversation

User, exact: "CMS-TDR-20 just landed"

Assistant, paraphrase: found the new CMS-TDR-020 CERNBox entry in the supplied
instructions, downloaded it and updated the catalogue and acquisition status.

## Decisions and outcomes

- Map CMS-TDR-020 to the initially suggested `CMS-MTD-TDR.pdf` filename.
- Acquire the supplied PDF: 63513920 bytes. Preserve SHA-256 and the updated
  instruction-file hash in a separate receipt; do not rewrite the initial receipt.
- Add SRC-CMS-TDR-020 to the manifest and update the reference guide. All five
  initially requested TDR labels now have local files; the catalogue has 14 entries.
- Title-page identity, canonical public URL, publication metadata and licensing
  remain unverified. No detector facts or approval states changed.

## Commands and validation

- `python3 tools/reference_downloads/download.py --only CMS-TDR-020 --receipt reference/downloads-2026-09-15-cms-mtd.json`: exit 0; acquired the PDF using the approved network workflow.
- `python3 -B -m unittest discover -s tools/reference_downloads -p 'test_*.py' -v`: exit 0; 4 tests passed.
- Inline Python checks: exit 0; independently recomputed the PDF SHA-256 and size,
  verified the PDF header and instruction-file hash, matched the manifest entry,
  and confirmed the PDF is ignored by Git and absent from the index.
- Session-record validation runs after completion of this entry.

## Changes and revision links

See the paired JSON inventory and `reference/downloads-2026-09-15-cms-mtd.json`.
The PDF remains local and ignored. Prior logs retain their historical statement
that this entry was missing at the time; this record resolves that follow-up.

## Follow-up

Bibliographic verification remains pending. Exact client version, model identity,
thread/turn IDs, token usage and invocation totals are unavailable.
