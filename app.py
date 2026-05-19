import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Eagles Academy Analytics", layout="wide")
st.title("Newcastle Eagles — Academy Analytics")
st.caption("U19 · 2024–25 season")

# ── Load data ──────────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    df = pd.read_csv("data/u19_stats.csv")
    df["eFG%"]   = (df["FGM"] + 0.5 * df["3PM"]) / df["FGA"] * 100
    df["TS%"]    = df["PTS"] / (2 * (df["FGA"] + 0.44 * df["FTA"])) * 100
    df["AST_TO"] = df["AST"] / df["TOV"].replace(0, 1)
    df["3P%"]    = df["3PM"] / df["3PA"].replace(0, 1) * 100
    return df

df = load_data()

# ── Sidebar ────────────────────────────────────────────────────────────────
st.sidebar.header("Filters")
selected_player = st.sidebar.selectbox("Select player", sorted(df["Player"].unique()))

player_df = df[df["Player"] == selected_player]

# ── Stat cards ─────────────────────────────────────────────────────────────
st.subheader("Season averages")
col1, col2, col3, col4 = st.columns(4)
col1.metric("Points per game", f"{player_df['PTS'].mean():.1f}")
col2.metric("eFG%",            f"{player_df['eFG%'].mean():.1f}")
col3.metric("AST/TO",          f"{player_df['AST_TO'].mean():.2f}")
col4.metric("Rebounds",        f"{player_df['REB'].mean():.1f}")

st.divider()

# ── Season trend ───────────────────────────────────────────────────────────
st.subheader("Season trend")

trend_stat = st.selectbox("Stat", {
    "Points per game": "PTS",
    "eFG%":            "eFG%",
    "AST/TO ratio":    "AST_TO",
    "Rebounds":        "REB",
}.keys())

stat_col = {"Points per game": "PTS", "eFG%": "eFG%", "AST/TO ratio": "AST_TO", "Rebounds": "REB"}[trend_stat]

fig_trend = px.line(
    player_df,
    x="Game",
    y=stat_col,
    markers=True,
    title=f"{trend_stat} — {selected_player}",
)
fig_trend.update_layout(plot_bgcolor="rgba(0,0,0,0)", xaxis_tickangle=-30)
st.plotly_chart(fig_trend, use_container_width=True)

st.divider()

# ── Best & worst opponents ─────────────────────────────────────────────────
st.subheader("Best & worst opponent performances")

opp_stat_label = st.selectbox("Rank opponents by", [
    "Points per game", "eFG%", "AST/TO ratio", "Rebounds"
])
opp_stat_col = {
    "Points per game": "PTS",
    "eFG%":            "eFG%",
    "AST/TO ratio":    "AST_TO",
    "Rebounds":        "REB",
}[opp_stat_label]

opponent_avgs = (
    player_df
    .groupby("Opponent")
    .agg(
        games   = ("Game",    "count"),
        PTS     = ("PTS",     "mean"),
        efg     = ("eFG%",    "mean"),
        ast_to  = ("AST_TO",  "mean"),
        REB     = ("REB",     "mean"),
    )
    .round(2)
    .reset_index()
)

col_map = {
    "Points per game": "PTS",
    "eFG%":            "efg",
    "AST/TO ratio":    "ast_to",
    "Rebounds":        "REB",
}
rank_col = col_map[opp_stat_label]

opponent_avgs = opponent_avgs[opponent_avgs["games"] == 2].copy()

n = min(2, len(opponent_avgs) // 2)
best  = opponent_avgs.nlargest(n,  rank_col).reset_index(drop=True)
worst = opponent_avgs.nsmallest(n, rank_col).reset_index(drop=True)

col_best, col_worst = st.columns(2)
with col_best:
    st.markdown("**Performed best against**")
    st.dataframe(best.rename(columns={"efg":"eFG%","ast_to":"AST/TO","PTS":"Pts","REB":"Reb"})[["Opponent","Pts","eFG%","AST/TO","Reb"]], hide_index=True, use_container_width=True)
with col_worst:
    st.markdown("**Performed worst against**")
    st.dataframe(worst.rename(columns={"efg":"eFG%","ast_to":"AST/TO","PTS":"Pts","REB":"Reb"})[["Opponent","Pts","eFG%","AST/TO","Reb"]], hide_index=True, use_container_width=True)

sorted_opps = opponent_avgs.sort_values(rank_col, ascending=False)
best_set  = set(best["Opponent"])
worst_set = set(worst["Opponent"])
colors = ["#1D9E75" if o in best_set else "#BA7517" if o in worst_set else "#888780" for o in sorted_opps["Opponent"]]

fig_opp = px.bar(
    sorted_opps,
    x="Opponent",
    y=rank_col,
    text=rank_col,
    title=f"{opp_stat_label} by opponent (2-game average)",
    labels={"Opponent": "", rank_col: opp_stat_label},
)
fig_opp.update_traces(marker_color=colors, texttemplate="%{text:.1f}", textposition="outside")
fig_opp.update_layout(plot_bgcolor="rgba(0,0,0,0)", showlegend=False, xaxis_tickangle=-30)
st.plotly_chart(fig_opp, use_container_width=True)

st.caption("Data shows the what — use the eye test to find the why.")

st.divider()

# ── 3&D squad map ──────────────────────────────────────────────────────────
st.subheader("3&D squad map")
squad_avgs = (
    df.groupby("Player")
    .agg(three_pct=("3P%", "mean"), def_rtg=("DEF_RTG", "mean"))
    .reset_index()
)
fig_scatter = px.scatter(
    squad_avgs,
    x="three_pct",
    y="def_rtg",
    hover_name="Player",
    text="Player",
    labels={"three_pct": "3PT%", "def_rtg": "Defensive rating"},
    title="3PT% vs Defensive rating — full squad",
)
fig_scatter.update_traces(textposition="top center")
fig_scatter.update_layout(plot_bgcolor="rgba(0,0,0,0)")
st.plotly_chart(fig_scatter, use_container_width=True)