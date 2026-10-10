# Minimal Cloud Run image for Heliopolis's Streamlit synthetic judge demo.
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    MPLCONFIGDIR=/tmp/heliopolis-matplotlib \
    HELIOPOLIS_DEMO_ONLY=1

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt \
    && useradd --create-home --uid 10001 heliopolis

COPY --chown=heliopolis:heliopolis . /app
USER heliopolis

EXPOSE 8080
# Cloud Run sets PORT. The app never binds directly to port 80/443.
CMD ["sh", "-c", "exec streamlit run app.py --server.address=0.0.0.0 --server.port=${PORT:-8080} --server.headless=true --browser.gatherUsageStats=false --server.enableXsrfProtection=true"]
