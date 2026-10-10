# Heliopolis-AI — Seven-Minute Spoken Rehearsal for the User's Latest Nine-Page Pitch

Source: uploaded \`Heliopolis_AI_MAIC_20261008_Main_Pitch (2)(1).pdf\` (nine slides, not the older ten-main-slide strategy and not the alternative nine-topic markdown pitch). This script follows each uploaded page in order. **No text or result below should be mistaken for current master's live output unless reproduced.**

**Rehearsal target:** 7 minutes total. The source PDF's cover prints “MAIC Semi-Final, 13 October 2026”; the assigned slot and allowed presentation duration must be confirmed from the organisers. Prepare an offline visual fallback before live demos. Stage materials may be locked independently of GitHub edits.

## Slide 1 | 0:00–0:20 | Solar screening before detailed studies

**Say:** Heliopolis-AI helps Malaysian solar-development teams bring land, electrical and project information into one early screening report. The aim is to show what needs checking before paying for detailed studies. We are not replacing the land office or the engineer.

**Cue:** Show the original photographic cover. Do not open a competing alternative deck.

## Slide 2 | 0:20–1:10 | One proposal, linked issues

**Say:** Here is a prepared Perak example with three parts: a land document, a single-line electrical diagram and project figures. The land record and the circuit are fictional test inputs; the financial scenario is illustrative. The point is not to pretend this is an actual approved site. The point is that an analyst must read these inputs together. A title exception and an electrical issue may remain unresolved even when the apparent cost of the project improves. Heliopolis aims to retain those connected questions in one review.

**Cue:** Point to the synthetic labels. This source diagram's sensing relay is drawn on a separate branch, not in the primary power route; **do not** interpret it as proof of an inline protected TNB-approved path.

## Slide 3 | 1:10–1:55 | What Gemini and the deterministic code do

**Say:** Google Gemini through Vertex AI extracts candidate document fields in the broader prototype. We have three saved synthetic OCR calls, not an independent accuracy benchmark. For this offline demonstration, we begin with reviewed input values. Python then checks ownership-share arithmetic, the represented electrical connections and the assumptions behind project economics. The output is one report of accepted inputs, findings and reviews still needed. Real-document extraction accuracy and time saved must be tested with independently checked examples.

**Cue:** Say “candidate extracted fields,” never “verified by AI” or “hallucination-free.”

## Slide 4 | 1:55–3:05 | Change an input; review remains

**Say:** Our saved prototype example begins at 3.21 megawatts AC, with a HOLD for expert review. The case then changes to two megawatts AC. The demonstration illustrates two things: accepted assumptions can change, and unresolved title and protection questions must remain visible. HOLD is not a rejected or approved solar project; it means independent review is still required. This specific saved screen belongs to the earlier prepared demonstration build. We must not claim that today's public GitHub version reproduced those numbers without running the same code and assumptions.

**Cue:** Prefer the actual uploaded slide's **saved screenshot** if the matching old working application is unavailable. Do not improvise a current-master “live rerun” that silently changes the storage rule/status wording.

## Slide 5 | 3:05–3:55 | Modelled costs and the storage caveat

**Say:** In these saved illustrative results, upfront cost falls from approximately 15.94 million to 7.06 million ringgit; discounted value improves from negative 9.79 million to negative 2.66 million. Neither case clears expert review. Importantly, 4.608 million ringgit of the change comes from a prototype storage assumption. This is not a pure capacity comparison, not evidence of a mandatory battery requirement, and not a bankable investment return. The useful result is transparency: the analyst sees what changed, what assumptions drove the calculation and what still needs independent checking.

**Cue:** Trace the grey and turquoise bars and read the disclaimer aloud. Do not say “we save RM8.88 million”.

## Slide 6 | 3:55–4:50 | Existing tools and local service alternatives

**Say:** We are not entering a market with no competitors. OpenSolar has a free core, while PVsyst and HelioScope sell different design and analysis licences. Malaysian consultancies such as NEMSolar and Solunar offer feasibility and engineering services. Their scopes are not identical, and we do not claim to be cheaper or technically superior. Our proposed opening is a combined early screening report: owner-share checks, represented circuit connectivity and project assumptions together. The original slide lists a three-thousand-ringgit annual Heliopolis offer. That is a proposed pricing experiment, not a sale or proven value.

**Cue:** Do not recite historical competitor prices as current quotations without checking them afresh.

## Slide 7 | 4:50–5:40 | Who would pay for the report?

**Say:** The first proposed buyer is a Malaysian solar developer or consultancy doing repeated early project reviews. The product is envisioned as a local installation licence at three thousand ringgit per year. It gives a structured report of the accepted inputs, reasons to review and missing evidence. We will evaluate it beside a qualified analyst using their normal tools on the same examples, measuring total preparation and correction time and what the buyer would actually pay. Seat limits, Vertex operating costs, installation support and customer demand remain open questions.

**Cue:** Point to RM3,000/year and say “proposed”; no signed customers have been established.

## Slide 8 | 5:40–6:25 | Review work, responsible impact

**Say:** The environmental and governance opportunity is earlier, better-targeted review. Land counsel must confirm title rights; an electrical reviewer checks actual protection; and a site survey validates ground conditions. The surface map shown here is illustrative, not surveyed terrain. In a real pilot we would count repeat site visits and studies actually avoided, including any extra checking the system creates. We cannot claim carbon reductions simply because software screens a possible future solar project. Any environmental benefit must be measured.

**Cue:** Point to the site map and its “illustrative surface data” label.

## Slide 9 | 6:25–7:00 | One connected review

**Say:** Heliopolis is intended as one connected first-pass review for land, electrical and project economics. We have built a demonstrable prototype, not an automated regulator. The next milestone is a small permissioned test: real documents with expert labels, a comparison with direct Vertex AI and a checklist, actual review effort and cost, and buyer feedback. If that evidence shows an improvement, we have a credible path to a usable product. Thank you.

**Cue:** Stay on the uploaded deck's exact Wudibei Lab closing slide. No new unvalidated scale or ESG figures.

---

## 75-second Q&A-only negative-control demonstration on current public master

The current GitHub \`app.py\` is a DIFFERENT application from the historical HOLD screenshots, but it can reliably demonstrate modern LV/MV modelled connection-path failures:
1. Preopen \`streamlit run app.py\`; choose a SYNTHETIC LSS site, \`Connection voltage class = MV\`.
2. In Electrical SLD Graph Audit, show the synthetic connected PV → inverter → relay → transformer → grid path. Scope: PRELIMINARY.
3. Turn off Connect Transformer to Grid while keeping the relay visible. The report must say \`NEEDS_REVIEW\`, not HOLD or TNB APPROVED.
4. The export status should match the displayed broken-path verdict.
5. Do NOT recalculate the uploaded slide's 3.21→2.00 costs on this build and pass them off as the same saved prototype numbers.

## Last checks

- [ ] Confirm organiser's actual time limit, date and whether slide submission is locked.
- [ ] Use the user's latest nine-page **visual** PDF, not PR #16's previous nine-section alternate.
- [ ] If speaking at 7 minutes, rehearse slide changes twice; leave a buffer.
- [ ] Display 186 offline Python test passes only with the exact public master CI link; do not replace older distinct local suites with ungrounded arithmetic.
- [ ] Keep private OCR inputs and Vertex credentials out of the public repository.
- [ ] If any live segment cannot be reproduced, use a clearly labelled saved screenshot and its matching version.
