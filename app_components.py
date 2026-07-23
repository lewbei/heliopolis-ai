"""Pure HTML / Markdown helper components used by the Streamlit app."""


def clean_html_markdown(html_str: str) -> str:
    """Strips leading whitespace from each line of a multiline HTML string
    to prevent Markdown parsers from interpreting indented lines as code blocks.
    """
    return "\n".join(line.strip() for line in html_str.splitlines())


def metric_card(label, value, delta=None, delta_type="up") -> str:
    """Return an HTML KPI metric card string (does not call st.*)."""
    cls = f"delta-{delta_type}"
    if delta_type == "up":
        arrow = "↑"
    elif delta_type == "down":
        arrow = "↓"
    else:
        arrow = "⚠"
    delta_html = f'<div class="metric-delta {cls}">{arrow} {delta}</div>' if delta else ""
    return clean_html_markdown(f"""
    <div class="metric-card">
        <div class="metric-label">{label}</div>
        <div class="metric-value">{value}</div>
        {delta_html}
    </div>
    """)


def status_badge(status: str) -> str:
    """Return a status badge span with green/amber/red styling."""
    status_clean = str(status).strip()
    if status_clean == "Approved":
        cls = "badge-green"
    elif status_clean in ("Flagged/Risky", "Flagged", "Risky"):
        cls = "badge-amber"
    elif status_clean == "Rejected":
        cls = "badge-red"
    else:
        cls = "badge-amber"
    return f'<span class="badge {cls}">{status_clean.upper()}</span>'


def owner_rows_html(owner_models) -> str:
    """Return the HTML <tr> rows for the owners table (owners only, no cumulative row)."""
    rows = "".join(
        f"""
    <tr>
        <td>{o.name}</td>
        <td><code>{o.ic_or_co_no}</code></td>
        <td><strong>{o.share_fraction}</strong></td>
        <td>{(o.calculated_share_float * 100.0):.2f}%</td>
    </tr>
        """
        for o in owner_models
    )
    return clean_html_markdown(rows)
