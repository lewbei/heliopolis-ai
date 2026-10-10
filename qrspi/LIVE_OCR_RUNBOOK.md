# Live Gemini OCR verification — user-controlled and privacy-sensitive

**Purpose:** Verify that Heliopolis can use Gemini on an **authorized** sample land title / electrical SLD without substituting a synthetic successful result. This is a workflow, not proof of general OCR accuracy.

## Requirements

- A valid local Google AI Studio API key or a permitted Vertex AI project. Google lists gemini-3.6-flash as a stable multimodal model; the exact deployment and access must be checked in the caller's account.
- One real or independently sourced example that you have the explicit right to send to the selected Google AI service; ideally a de-identified permitted title/SLD with human-reviewed reference fields.
- Never send sensitive account numbers, MyKad/NRIC or identifiable owner's data in chat. Do not put an API key in GitHub code, issue text, CI logs, markdown, or the benchmark CSV.
- If no permitted document or provider access exists, **stop**: this is not ready to be marked "tested" or "100% accurate".

## Run the local smoke test

From the repo root, in your own protected environment:

    pip install -r requirements.txt
    # Set GEMINI_API_KEY locally in .env (ignored by git) or an approved Vertex project.
    python verify_live_ocr.py --title /approved/path/example.png --confirm-cloud-processing

For an SLD:

    python verify_live_ocr.py --sld /approved/path/diagram.png --confirm-cloud-processing

The flag is **intentional user permission** to transmit the image externally. Without it, the tool refuses transmission; without the API key, it fails before OCR. An unsuccessful parser returns NEEDS_REVIEW and a nonzero exit code, not a dummy Geran/SLD. Each real run may consume API resources; run only with appropriate consent.

The terminal output contains only a SHA-256 hash, schema/review status, node/owner counts and configured model, **not extracted names/NRICs or the raw image**. It is still a verification record and must be stored securely. To save the sanitized audit add:

    --output /secure/local/heliopolis_ocr_audit.json

Do NOT commit your source images or private output logs to a public repository.

## Required human QA checklist

1. Verify file SHA-256, source, consent/permission and configured provider/model version.
2. Compare each extracted title/lot/state, metric and imperial area, all owners and shares, caveats/charges/reserve flag against the **actual page**. A returned model object means JSON parsed, NOT that its fields are correct.
3. Compare SLD recognized symbols, bounding boxes, wire segment endpoints, crossings without junction dots, relays and transformer/grid paths to the original drawing. A graph pass is NOT proof of an approved protection configuration.
4. Record counts of corrected/missed fields, API calls/tokens, latency, model version, cost, invalid JSON, abstention and reviewer minutes.
5. Do not count any failed parser as a correct negative; log as failure/abstention. Use the matched evaluation protocol in BENCHMARK_RUNBOOK.md only when all three real methods are executed and independent reference labels exist.

**Current status:** No consented customer titles/SLDs, live API credentials or independent human labels were supplied to the assistant. Consequently real-document extraction and real OCR field accuracy remain UNVERIFIED. Issue #7 cannot honestly be closed until a permitted live sample and human comparison are performed.
