import pandas as pd
import plotly.graph_objs as go
from pathlib import Path

# 1) Read Excel
xls = pd.ExcelFile("LIVE_PNL.xltm")
df_table = pd.read_excel(xls, sheet_name="TABLE")

# 2) Build a Plotly chart
fig = go.Figure()
fig.add_trace(go.Scatter(
    x=df_table["Time"], y=df_table["LIVE_PNL"],
    mode="lines+markers", name="PnL"
))
fig.update_layout(
    title="Live P&L over Time",
    xaxis_title="Time", yaxis_title="P&L"
)

# 3) Create HTML
html = f"""
<html>
  <head><title>Static P&L Dashboard</title></head>
  <body>
    <h1>Live P&L Dashboard</h1>
    {fig.to_html(full_html=False, include_plotlyjs='cdn')}
  </body>
</html>
"""

# 4) Write out to docs/index.html
out = Path("docs/index.html")
out.parent.mkdir(exist_ok=True)
out.write_text(html, encoding="utf-8")
print("Generated docs/index.html")
