import pandas as pd
import plotly.graph_objs as go
from pathlib import Path
from datetime import datetime

EXCEL_PATH = "LIVE_PNL.xltm"

# ─── READ CHART METRICS ─────────────────────────────────────────────
def load_metrics():
    df = pd.read_excel(EXCEL_PATH, sheet_name="CHART", header=None)
    metrics = {
        "LIVE%":    df.iat[0, 0],
        "MAX%":     df.iat[0, 1],
        "MIN%":     df.iat[0, 2],
        "LIVE_PNL": df.iat[0, 3],
        "SPOT":     df.iat[0, 5],
        "MARGIN":   df.iat[0, 7],
        "TIME":     df.iat[0,10],
    }
    for k in ("LIVE%", "MAX%", "MIN%"):
        try:
            metrics[k] = float(metrics[k]) * 100
        except Exception:
            metrics[k] = 0.0
    return metrics

# ─── READ TABLE FOR CHART ───────────────────────────────────────────
def load_table():
    df = pd.read_excel(EXCEL_PATH, sheet_name="TABLE", header=1)
    df = df.rename(columns={
        df.columns[0]: "Time",
        df.columns[1]: "LIVE_PNL",
        df.columns[2]: "SPOT"
    })
    return df

# ─── BUILD PLOTLY CHART ─────────────────────────────────────────────
def make_figure(df):
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df["Time"], y=df["LIVE_PNL"],
        mode="lines", fill="tozeroy",
        name="LIVE PNL", line=dict(color="white", width=2),
    ))
    fig.add_trace(go.Scatter(
        x=df["Time"], y=df["SPOT"],
        mode="lines", name="SPOT",
        yaxis="y2", line=dict(color="black", width=2),
    ))
    fig.update_layout(
        template="plotly_dark",
        plot_bgcolor="#385e9d",
        paper_bgcolor="#385e9d",
        hovermode="x unified",
        xaxis=dict(title="Time", type="category", tickangle=-45, tickfont=dict(size=10), showgrid=False),
        yaxis=dict(title="LIVE PNL", zerolinecolor="white"),
        yaxis2=dict(title="SPOT", overlaying="y", side="right"),
        margin=dict(l=40, r=40, t=30, b=80),
        legend=dict(bgcolor="rgba(0,0,0,0)")
    )
    return fig.to_html(full_html=False, include_plotlyjs='cdn')

# ─── HTML METRIC CARDS ──────────────────────────────────────────────
def build_metric_cards(metrics):
    metric_order = ["LIVE%", "MAX%", "MIN%", "LIVE_PNL", "SPOT", "MARGIN", "TIME"]
    cards_html = '<div style="display:flex; gap:10px; flex-wrap:wrap;">\n'

    for key in metric_order:
        raw = metrics.get(key, "--")
        if isinstance(raw, (int, float)):
            text = f"{raw:,.2f}"
        else:
            text = str(raw)
        if key in ("LIVE%", "MAX%", "MIN%"):
            text += "%"
        color = "crimson" if text.startswith("-") else "#2c3e50"

        cards_html += f"""
        <div style="flex:1; padding:10px; background:#fff; border-radius:6px;
                    box-shadow:0 1px 3px rgba(0,0,0,0.2); text-align:center; min-width:100px">
            <div style="font-size:22px; font-weight:bold; color:{color}">{text}</div>
            <div style="font-size:12px; color:#555">{key}</div>
        </div>
        """
    cards_html += '</div>'
    return cards_html

# ─── MAIN SCRIPT ────────────────────────────────────────────────────
df    = load_table()
metrics = load_metrics()
fig_html = make_figure(df)
cards_html = build_metric_cards(metrics)
last_updated = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# ─── FINAL HTML ─────────────────────────────────────────────────────
html = f"""
<html>
  <head>
    <title>Live P&L Dashboard</title>
    <meta charset="utf-8" />
    <meta http-equiv="refresh" content="30">
    <style>
      body {{ font-family: Arial; background: #f5f5f5; padding: 20px; }}
      .header {{ text-align: center; margin-bottom: 10px; }}
      .timestamp {{ text-align: center; font-size: 12px; color: #555; margin-bottom: 20px; }}
    </style>
  </head>
  <body>
    <h2 class="header">📈 Live P&L Dashboard</h2>
    <div class="timestamp">Last updated: {last_updated}</div>
    {cards_html}
    <div style="padding-top:20px;">{fig_html}</div>
  </body>
</html>
"""

# Write to docs/index.html
out = Path("docs/index.html")
out.parent.mkdir(exist_ok=True)
out.write_text(html, encoding="utf-8")
print("✅ Dashboard generated at docs/index.html")
