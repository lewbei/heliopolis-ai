# MAIC Nexus T1 — AI Usage and Third-Party Dependencies (DRAFT CORRECTION)

Project: Heliopolis-AI — AI-assisted preliminary solar project document screening.
Track: T1 AI for Clean Energy.
Status: Proposed disclosure correction for organizer review. Do not replace a submission during a locked judging window without permission.

## 1. Where AI is actually used

Google's **Gemini multimodal model accessed via Google Vertex AI** is used for optional OCR-like extraction of title fields and electrical SLD objects/wiring. This model is a third-party commercial foundation model, NOT an open-source model created, pretrained, fine-tuned or owned by this team.

The demo can also run synthetic local inputs without an external AI call. Synthetic demo outputs are NOT evidence of model OCR accuracy.

Deterministic Python performs the following limited operations after extraction:
- unit/fraction calculations and preliminary visible-title restrictions;
- NetworkX modeled LV/MV SLD connectivity and visible anti-islanding annotation screens;
- synthetic slope/energy inputs, limited grid MW/MVA sensitivity and indicative LSS financial calculations;
- independent Solar ATAP non-domestic monthly energy-credit arithmetic with explicit user supplied or synthetic inputs.

These rules may reject inconsistent fields and inappropriate calculations, but DO NOT ELIMINATE model hallucinations or guarantee civil, legal, financial or electrical correctness. A false extracted field or wire may still pass some validators; human review remains mandatory.

## 2. Frameworks and licensed software

- Google Vertex AI / Gemini: managed third-party AI service, Google terms and account permissions apply. Authentication should use a scoped managed service account for hosted deployment. No model licence/weights are transferred to Heliopolis.
- NetworkX, NumPy, Pydantic, Streamlit, Matplotlib, Plotly, Pillow, google-genai, python-dotenv: third-party libraries/packages used by the prototype; inspect each applicable version/licence and security advisories before commercialization.
- Project-specific glue and tests are contained in the public repository. The team has also used generative AI assistance to draft/refine parts of implementation and documentation; all such outputs require review and testing. Do not imply independent code authorship verification by a patent examiner.

## 3. Actual evidence

- The latest confirmed master workflow at this draft review is 186 offline Python tests passing plus synthetic CLI JSON and Streamlit smoke checks. These are SOFTWARE regression results only.
- The 500 site registry entries and terrain surfaces are synthetic illustrations, not government-verified cadastral records or observed site surveys.
- No separately measured real title/SLD OCR field accuracy, no statistically meaningful false-clearance rate, no customer time savings and no positive commercial traction have been verified.
- LSS PPA IRR is an illustrative sensitivity; no signed tariff or utility clearance exists. Historical NOVA and self-consumption financial ROI are withheld without load/tariff evidence. The Solar ATAP energy-only monthly screen is not a full utility invoice or financial projection.

## 4. Privacy, security and intellectual property

- The application asks for explicit authorization before sending real uploaded documents to the selected Google cloud provider. This checkbox is NOT enterprise IAM or a substitute for legal consent and access controls.
- Do not publish raw ownership records, NRICs, customer bills or API secrets on GitHub. Any enterprise offering must add authentication, tenant isolation, encrypted temporary storage, retention/deletion controls, quota/rate limits, supplier data processing review and a professional Malaysian PDPA assessment.
- Patent landscape/search notes and module provenance are PRELIMINARY; **no complete freedom-to-operate legal opinion has been obtained**, and no copyright/non-infringement guarantee can honestly be made. Mathematical expressions are not a blanket exemption from IP or software licence obligations.
- The team does not claim TNB, SEDA, land-office, professional engineering or legal certification.

## 5. Public-source traceability

Primary code: https://github.com/lewbei/heliopolis-ai
Regulatory context: https://www.seda.gov.my/reportal/atap/
Competition disclosure requirements: https://www.maicnexus.com/en/terms

The user remains responsible for verifying this disclosure and the specific use of AI tools/models in the submitted artifact. This document does not replace the organisers' official form or participation agreement.
