import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import pandas as pd
import plotly.graph_objs as go

# ─── CONFIG ───────────────────────────────────────────────────────────────
EXCEL_PATH = "LIVE_PNL.xltm"
# exact order you want them displayed
METRIC_ORDER = ["LIVE%", "MAX%", "MIN%", "LIVE_PNL", "SPOT", "MARGIN", "TIME"]

# ─── DATA LOADING ─────────────────────────────────────────────────────────
def load_data():
    # read your TABLE sheet (header row may be at row 2—adjust header=1 if needed)
    df = pd.read_excel(EXCEL_PATH, sheet_name="TABLE", header=1)
    # rename first three columns explicitly
    df = df.rename(columns={
        df.columns[0]: "Time",
        df.columns[1]: "LIVE_PNL",
        df.columns[2]: "SPOT"
    })
    # parse Time strictly as time, keep only the string HH:MM:SS
    df["Time"] = pd.to_datetime(df["Time"], format="%H:%M:%S").dt.strftime("%H:%M:%S")
    return df

def load_metrics():
    # Read CHART sheet without headers
    df = pd.read_excel(EXCEL_PATH, sheet_name="CHART", header=None)

    # Map specific cells to your metrics
    metrics = {
        "LIVE%": df.iat[0, 0],    # A1
        "MAX%": df.iat[0, 1],     # B1
        "MIN%": df.iat[0, 2],     # C1
        "LIVE_PNL": df.iat[0, 3], # D1
        "SPOT": df.iat[0, 5],     # F1
        "MARGIN": df.iat[0, 7],   # H1
        "TIME": df.iat[0, 10],    # K1
    }

    return metrics

# ─── CHART CREATION ───────────────────────────────────────────────────────
def make_figure(df):
    fig = go.Figure()
    # LIVE_PNL area + line
    fig.add_trace(go.Scatter(
        x=df["Time"], y=df["LIVE_PNL"],
        mode="lines", fill="tozeroy",
        name="LIVE PNL", line=dict(color="white", width=2),
    ))
    # SPOT on secondary axis
    fig.add_trace(go.Scatter(
        x=df["Time"], y=df["SPOT"],
        mode="lines", name="SPOT",
        yaxis="y2", line=dict(color="black", width=2),
    ))

    fig.update_layout(
        # dark / deep‑blue background
        template="plotly_dark",
        plot_bgcolor="#385e9d",
        paper_bgcolor="#385e9d",
        hovermode="x unified",
        xaxis=dict(
            title="Time",
            type="category",         # treat times as categories to avoid dates
            tickangle= -45,
            tickfont=dict(size=10),
            showgrid=False,
        ),
        yaxis=dict(
            title="LIVE PNL",
            zerolinecolor="white",
        ),
        yaxis2=dict(
            title="SPOT",
            overlaying="y", side="right",
        ),
        margin=dict(l=40, r=40, t=30, b=80),
        legend=dict(bgcolor="rgba(0,0,0,0)"),
    )
    return fig

# ─── DASH APP ─────────────────────────────────────────────────────────────
app = dash.Dash(__name__)
app.layout = html.Div(style={"fontFamily":"Arial"}, children=[
    html.H2("📈 Live P&L Dashboard", style={"textAlign":"center", "margin":"10px 0"}),
    # metrics cards container
    html.Div(id="metrics-row", style={
        "display":"flex", "gap":"10px",
        "padding":"0 20px", "marginBottom":"20px"
    }),
    # chart
    html.Div(dcc.Graph(id="live-chart"), style={"padding":"0 20px"}),
    # auto-refresh
    dcc.Interval(id="interval", interval=5000, n_intervals=0)
])

# ─── CALLBACK ────────────────────────────────────────────────────────────
@app.callback(
    [Output("metrics-row", "children"),
     Output("live-chart", "figure")],
    Input("interval", "n_intervals")
)
def update_dashboard(n):
    # reload data & metrics
    df = load_data()
    metrics = load_metrics()

    # build a card for each metric
    cards = []
    for key in METRIC_ORDER:
        val = metrics.get(key, "--")
        cards.append(
            html.Div([
                html.Div(str(val), style={
                    "fontSize":"22px", "fontWeight":"bold",
                    "color":"crimson" if str(val).startswith("-") else "#2c3e50"
                }),
                html.Div(key, style={"fontSize":"12px", "color":"#555"})
            ], style={
                "flex":"1", "padding":"10px",
                "backgroundColor":"#fff", "borderRadius":"6px",
                "boxShadow":"0 1px 3px rgba(0,0,0,0.2)",
                "textAlign":"center"
            })
        )

    fig = make_figure(df)
    return cards, fig

# ─── RUN ─────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)
