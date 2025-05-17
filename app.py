import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import pandas as pd
import plotly.graph_objs as go

# ─── CONFIG ───────────────────────────────────────────────────────────────
EXCEL_PATH   = "LIVE_PNL.xltm"
METRIC_ORDER = ["LIVE%", "MAX%", "MIN%", "LIVE_PNL", "SPOT", "MARGIN", "TIME"]

# ─── DATA LOADING ─────────────────────────────────────────────────────────
def load_data():
    df = pd.read_excel(EXCEL_PATH, sheet_name="TABLE", header=1)
    df = df.rename(columns={
        df.columns[0]: "Time",
        df.columns[1]: "LIVE_PNL",
        df.columns[2]: "SPOT"
    })
    df["Time"] = pd.to_datetime(df["Time"], format="%H:%M:%S").dt.strftime("%H:%M:%S")
    return df

def load_metrics():
    df = pd.read_excel(EXCEL_PATH, sheet_name="CHART", header=None)
    # read exactly A1, B1, C1, D1, F1, H1, K1
    metrics = {
        "LIVE%":    df.iat[0, 0],
        "MAX%":     df.iat[0, 1],
        "MIN%":     df.iat[0, 2],
        "LIVE_PNL": df.iat[0, 3],
        "SPOT":     df.iat[0, 5],
        "MARGIN":   df.iat[0, 7],
        "TIME":     df.iat[0,10],
    }
    # Excel stores formatted 0.05% as 0.0005 under the hood, so multiply by 100
    for k in ("LIVE%", "MAX%", "MIN%"):
        try:
            metrics[k] = float(metrics[k]) * 100
        except Exception:
            metrics[k] = 0.0
    return metrics

# ─── CHART CREATION ───────────────────────────────────────────────────────
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
        xaxis=dict(
            title="Time", type="category",
            tickangle=-45, tickfont=dict(size=10),
            showgrid=False
        ),
        yaxis=dict(title="LIVE PNL", zerolinecolor="white"),
        yaxis2=dict(title="SPOT", overlaying="y", side="right"),
        margin=dict(l=40, r=40, t=30, b=80),
        legend=dict(bgcolor="rgba(0,0,0,0)")
    )
    return fig

# ─── DASH APP ─────────────────────────────────────────────────────────────
app = dash.Dash(__name__)
app.title = "Live P&L Dashboard"

app.layout = html.Div(style={"fontFamily":"Arial"}, children=[
    html.H2("📈 Live P&L Dashboard", style={"textAlign":"center", "margin":"10px 0"}),

    html.Div(id="metrics-row", style={
        "display":"flex", "gap":"10px",
        "padding":"0 20px", "marginBottom":"20px"
    }),

    html.Div(dcc.Graph(id="live-chart"), style={"padding":"0 20px"}),

    dcc.Interval(id="interval", interval=5000, n_intervals=0)
])

# ─── CALLBACK ────────────────────────────────────────────────────────────
@app.callback(
    [Output("metrics-row", "children"),
     Output("live-chart", "figure")],
    Input("interval", "n_intervals")
)
def update_dashboard(n):
    df = load_data()
    metrics = load_metrics()

    cards = []
    for key in METRIC_ORDER:
        raw = metrics.get(key, "--")
        # format numbers to two decimals
        if isinstance(raw, (int, float)):
            text = f"{raw:,.2f}"
        else:
            text = str(raw)
        # add % sign
        if key in ("LIVE%", "MAX%", "MIN%"):
            text += "%"
        color = "crimson" if text.startswith("-") else "#2c3e50"

        cards.append(
            html.Div([
                html.Div(text, style={
                    "fontSize":"22px", "fontWeight":"bold", "color":color
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
