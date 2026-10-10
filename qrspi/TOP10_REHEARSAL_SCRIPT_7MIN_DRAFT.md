# Heliopolis-AI — 7-Minute Semifinal Rehearsal Script (DRAFT)

Prepared 10 October 2026. Based on the proposed NINE-topic pitch in PITCH_DECK.md and current public master, NOT the older 7 October v8 / 8 October local working build.

**Timing:** 7:00 total spoken/demo target. Only assume an 8-minute total allotment if the organizer confirms it. The nine source slide headings may render as TEN physical PDF pages because one section paginates; verify your remote control cues against the rendered PDF and rehearse with a stopwatch.

**Competition restrictions:** If the semifinal review period is locked, do NOT replace submitted materials without written approval. This is a private rehearsal artifact, not the approved stage deck.

## 1. Opening | 0:00–0:20 (20 seconds)

**Spoken:** A solar project can look promising until the documents disagree. Before detailed engineering, developers need to reconcile land rights, electrical diagrams and project assumptions. Heliopolis-AI is an independent Malaysian preliminary screening tool that highlights what needs review. It does not approve a project.

**Cue:** Point to the buyer workflow, not a claim of time savings.

## 2. The document bottleneck | 0:20–1:00 (40 seconds)

**Spoken:** Our first buyer is a project-development analyst at a Malaysian solar EPC or independent power producer. A land title may contain unclear areas or multiple owners. An electrical drawing may show incomplete wiring or protection evidence. Energy-programme assumptions can also be mixed up. These documents are normally reconciled before expensive due diligence. We combine selected early checks in one report, so the specialist can see accepted information and unresolved issues. This is a product hypothesis; we still need to measure whether it reduces correction time and missed critical findings.

**Cue:** Keep one buyer and one task. Do not promise automated permitting.

## 3. What AI actually does | 1:00–1:45 (45 seconds)

**Spoken:** The AI role is narrowly defined. We use a Google Gemini multimodal model through Vertex AI for optional extraction of scanned title fields and SLD symbols and wires. Python then checks arithmetic, missing fields, title restrictions and modeled drawing connections. Financial calculations are also deterministic. If a critical field is missing or an uploaded image cannot be read, the program asks for human review; it must never pretend the image was a successful synthetic example. What you will see next uses intentionally synthetic data so the demonstration is reproducible without cloud credentials.

**Cue:** Show source labels clearly. No live Vertex request unless a permissioned sample has been rehearsed.

## 4. Reproducible negative-control demo | 1:45–3:00 (75 seconds)

**Spoken:** This is a fictional Malaysian project, not a real land-office record. I select a modeled medium-voltage connection and the illustrative LSS PPA financial case. The drawing initially shows a modeled photovoltaic array, inverter, anti-islanding relay, transformer and grid connection. A preliminary connected path is visible. That does not mean TNB approval. Now I disconnect the transformer from the grid, but leave the relay present. The system returns NEEDS_REVIEW. A relay existing somewhere on a drawing is not enough; the modeled protection path has to connect. The downloaded JSON can be checked against this displayed finding. Our result is an issue list for an engineer, not a compliance certificate.

**Cue, rehearse 75-second sequence:** 0–10 switch to PRE-OPENED Streamlit; 10–25 select explicit MV if not already; 25–40 show normal modeled graph; 40–55 disable "Connect Transformer to Grid"; 55–65 show NEEDS_REVIEW; 65–75 show the report field, then switch back. Avoid a fresh OCR call. Have screenshots of both states as a fallback.

## 5. Difference from alternatives | 3:00–3:45 (45 seconds)

**Spoken:** The competition is serious. PVcase and Glint Solar address site search, parcel and grid constraints. RatedPower performs much deeper plant design and energy modeling. We do not claim to replace them. Our smaller entry point is document triage: interpreting the incoming Malaysian title and electrical drawings before that detailed work. A direct Vertex AI call followed by a spreadsheet is another valid alternative. Our validators must prove they catch important mistakes beyond that cheap baseline. Today that incremental improvement has not been established on independently labeled real documents.

**Cue:** Acknowledge alternatives; never say "first", "only" or "most accurate".

## 6. Regulatory and engineering limits | 3:45–4:25 (40 seconds)

**Spoken:** The prototype separates what it can calculate from what needs an expert. Ownership shares are not a legal right to lease the whole parcel. A passing electrical graph does not certify inverter anti-islanding tests or relay settings. Low-voltage drawings can differ from medium-voltage diagrams; we screen those paths separately. Our LSS financial calculation is an illustration without a signed power purchase agreement. Solar ATAP is another, separate consumer scheme for which we implement only a limited monthly energy-charge calculation, not a complete TNB bill or 21-year investment return.

**Cue:** Avoid making the ATAP page a second main product.

## 7. Evidence and next test | 4:25–5:10 (45 seconds)

**Spoken:** The publicly verified master build passed 186 offline Python regression tests, and CI also checked an illustrative JSON report and Streamlit startup. Those tests cover code paths and deliberate failure cases; they do not establish field OCR accuracy. We have a paired evaluation protocol for direct Gemini, Gemini with a simple checklist and Heliopolis, but it awaits real, permissioned documents and independent reference labels. We would report false clearances, how often the system abstains, actual correction minutes and cost per analyzed dossier. If the simple approach is just as good, we should simplify rather than claim an unsupported advantage.

**Cue:** State the exact current-master test count; do not mix older 232 + 39 local counts.

## 8. Who pays, and scale | 5:10–6:05 (55 seconds)

**Spoken:** Our initial customer is an EPC or IPP analyst responsible for repeated first-pass reviews. The prior commercial proposal is a local installation licence at three thousand ringgit per year. That price is only a test of willingness to pay; we have no confirmed sales. The real equation is measured analyst hours saved and critical issues caught, minus correction effort, Vertex API use, hosting and support. Technically, we would first validate the standalone Python app in a controlled private deployment using a scoped Vertex service account. Only then would we add authenticated dossier queues, cost quotas, human review and separately verified state-specific rules. Thousands of users and nationwide registry integrations are not operating today.

**Cue:** A concrete staged scale model; no fake customer/partner logos.

## 9. Responsible ESG and request | 6:05–7:00 (55 seconds)

**Spoken:** Environmental benefit is a question to measure: could earlier recognition of unsuitable land or missing constraints avoid needless studies or repeated trips? The software itself produces no renewable electricity, and we claim zero verified avoided tonnes of carbon. Socially, it should keep co-owner and land-rights concerns visible for professional consent review, without publishing private documents. Governance is the strongest current mechanism: source labels, visible assumptions and explicit review flags instead of a false approval. We ask for a small, consented three-to-five-site exploratory pilot with independent reviewers and a comparison against the existing workflow. That will tell us whether Heliopolis deserves a place alongside the tools solar developers already use. Our commitment is measurable evidence before commercialization.

**Cue:** End by 7:00. If the official limit is 8:00, retain the extra minute as contingency rather than filling it with new features.

---

## Fallback when the demo does not respond

Say: "The live demonstration has not completed, so I will show the saved synthetic input and corresponding output from our tested build. The connected example only passes a preliminary path check; the deliberately broken connection must return NEEDS_REVIEW." Show a prepared screenshot labeled **SYNTHETIC / OFFLINE**, without inventing a live Vertex result.

## Strict version-control rehearsal gate

Do not mix the newer master application with the old October 7–8 3.21-to-2.00 MW / HOLD comparison, RM4.608m storage-effect claim or 232 Python/API +39 frontend count. Those belong to an earlier LOCAL candidate until reproduced independently on the exact build. Do not mix an alternative nine-slide PDF with the existing submitted deck during a notified stage lock.

## Final on-stage preflight

- Confirm exact date, presentation length, agreement, artifact links and whether the judging review window is locked via the official MAIC dashboard/email.
- Freeze ONE script, ONE exact deck, ONE app commit, ONE saved synthetic case and matching JSON/screenshots.
- Pre-run the Streamlit app, explicitly select MV, verify the normal graph then broken-transformer NEEDS_REVIEW, and test the fallback.
- Verify the PDF is at most 12 physical pages and 5 MB and the written summary at most 500 words.
- Rehearse the sequence twice with a clock before changing any stage materials.
