# Heliopolis-AI — Public synthetic-only Cloud Run deployment

**Status:** tested configuration proposal, NOT an assertion that a live site has already been deployed. 10 October 2026.

## Public versus private

The public MAIC Streamlit website MUST run with HELIOPOLIS_DEMO_ONLY=1. In this mode:
- Main land/SLD page creates NO PNG/JPG file-upload widgets or OCR permission control, and cannot send document scans to Gemini/Vertex AI.
- Separate Solar ATAP page uses ONLY the clearly synthetic example, NO CSV upload or customer billing record.
- The site displays prominently that only SYNTHETIC demonstration inputs are used, not genuine land title or grid project evidence.
- Public Cloud Run service account has NO Vertex AI permission. The public server NEVER receives a Google API key or credential file.

The committed Dockerfile defaults to HELIOPOLIS_DEMO_ONLY=1, uses a non-root Linux user and runs Streamlit on Cloud Run's assigned PORT. The .dockerignore excludes .env, key material, scanned documents, presentations, generated reports, test outputs and Git metadata.

**Judge demonstration:** Select Standard Presets → MAIC 2026 Source Title (2-acre SYNTHETIC). The prepared original Slide-2 title has two fictional owners (60/120 each), caveat, 2 acres, and MV auxiliary anti-islanding relay; neither 3.21 nor 2.00 MWac should be presented as land-area feasible under the illustrative density. The output remains NEEDS_REVIEW. For a deliberate connectivity failure, switch to the SEPARATE "Perak Site (Default High Slope)" fixture, set MV and turn off Connect Transformer to Grid. These are DIFFERENT fictional site inputs: don't conflate them.

## Prerequisites

- A Google Cloud project with billing enabled; permissions to enable Cloud Run, Cloud Build and Artifact Registry and to create and use service accounts.
- gcloud CLI installed and signed in locally as an authorized human (gcloud auth login).
- Review the stage's specific allowed demo URL, access and timing. Pick one approved region; the example below uses asia-southeast1 (Singapore), **not Malaysian data residency**.
- Freeze a tested Git SHA; don't use an untested change immediately before judging.

## Test locally first

    python -m pip install -r requirements.txt
    HELIOPOLIS_DEMO_ONLY=1 streamlit run app.py --server.address=127.0.0.1 --server.port=8501

Open http://localhost:8501. Confirm NO uploads anywhere in the sidebar or Solar ATAP page.

Docker smoke:

    docker build -t heliopolis-maic-demo:local .
    docker run --rm -e HELIOPOLIS_DEMO_ONLY=1 -e PORT=8080 -p 8080:8080 heliopolis-maic-demo:local

Open http://localhost:8080 and retest the two synthetic scenarios. No credentials are required in either case.

## Deploy explicitly with the authorized Google Cloud account

From a checkout of the tested repository revision:

    PROJECT_ID=your-project-id
    REGION=asia-southeast1
    ACCOUNT=heliopolis-public-demo

    gcloud config set project "$PROJECT_ID"
    gcloud services enable run.googleapis.com cloudbuild.googleapis.com artifactregistry.googleapis.com

Create dedicated PUBLIC runtime identity with NO Vertex/Storage/Editor permissions:

    gcloud iam service-accounts create "$ACCOUNT" \
        --display-name="Heliopolis public synthetic demo; no Vertex permissions"

Deploy:

    gcloud run deploy heliopolis-demo \
        --source . \
        --project "$PROJECT_ID" \
        --region "$REGION" \
        --allow-unauthenticated \
        --service-account "$ACCOUNT@$PROJECT_ID.iam.gserviceaccount.com" \
        --set-env-vars HELIOPOLIS_DEMO_ONLY=1 \
        --memory=1Gi \
        --cpu=1 \
        --min-instances=0 \
        --max-instances=2 \
        --concurrency=8 \
        --timeout=120

Note: Deploying from source uses a build identity and may require separate Google Cloud Build and Artifact Registry IAM setup. Keep the PUBLIC runtime identity unprivileged. Do NOT grant the public identity Vertex AI permissions or substitute a powerful default Compute Engine Editor account to silence build errors.

Find the URL:

    gcloud run services describe heliopolis-demo \
        --region "$REGION" --project "$PROJECT_ID" \
        --format='value(status.url)'

**No Cloud Run URL has been verified yet.** The GitHub connector can prepare code but has no authority to deploy to your Cloud project.

## Go/no-go release checks

1. Public URL opens anonymously in incognito and from a phone on another network.
2. Main app and Solar ATAP page show PUBLIC SYNTHETIC DEMO; there are no upload controls.
3. Source-faithful MAIC synthetic title preset loads 2 acres and the same two fictional owners and caveat; it never silently substitutes the 12-acre Perak fixture.
4. Main MV SLD has a sensing/control auxiliary relay, so protection is not falsely approved. Source-title footprint mismatch is visible at 3.21 and 2.00 MWac.
5. Separate synthetic MV toggle case changes from preliminary protected path to NEEDS_REVIEW when transformer-to-grid is disconnected.
6. Download JSON agrees with on-screen input, source identifiers, voltage class and verdict.
7. Reloads, two browser sessions, a cold start and connectivity interruption have a safe, rehearsed fallback.
8. Inspect Cloud Run logs and Google Cloud billing to ensure no raw customer identities and NO Vertex OCR charges.
9. No actual project approval, verified avoided CO2, customer savings or contract is claimed.

Maximum instances and billing budgets are safeguards, NOT a guaranteed hard spending ceiling.

## Private Vertex AI service — later, not anonymously public

Use the same deterministic Python screening engine in a DIFFERENT, authenticated single-tenant service only after actual access control/IAP, per-user quotas, content size/format limits, safe temporary storage, redacted error logs, deletion/retention and an appropriate processing agreement are implemented.

A private Cloud Run service should run with HELIOPOLIS_DEMO_ONLY=0, GOOGLE_CLOUD_PROJECT set, chosen supported region/model, and its OWN user-managed service account with minimum Vertex AI permissions. Cloud Run supplies Application Default Credentials through its runtime identity. Never commit .env or JSON credentials to GitHub or publish the private file-upload URL. A checkbox alone does not authenticate users.

No automatic customer onboarding, storage database, job queue or API billing settlement is claimed to exist today. Those belong to a 30/60/90-day staged private beta after real-world evidence.

## Official references

- Streamlit on Cloud Run: https://docs.cloud.google.com/run/docs/quickstarts/build-and-deploy/deploy-python-streamlit-service
- Cloud Run service identity: https://docs.cloud.google.com/run/docs/securing/service-identity
- Cloud Run source deployments: https://docs.cloud.google.com/run/docs/deploying-source-code
- Cloud Run max instances: https://docs.cloud.google.com/run/docs/configuring/max-instances
- Billing budgets and limitations: https://docs.cloud.google.com/billing/docs/how-to/budgets-spend-caps
