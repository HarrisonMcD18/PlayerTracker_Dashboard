import streamlit as st
import pandas as pd
import plotly.express as px
import os
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import Arc, Circle, Rectangle, FancyArrowPatch
from matplotlib.colors import LinearSegmentedColormap

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

# ── Zone chart ─────────────────────────────────────────────────────────────── 
st.divider()
st.subheader("Shot zone chart")
 
SHOT_FILE = "data/shot_data.csv"
 
# Define zones with their court coordinates (centre x, centre y) and polygon bounds
# Court is 500 wide x 470 tall (NBA standard units, origin at basket)
ZONE_DEFS = {
    "Restricted Area":  {"x": 0,    "y": 60,   "label": "RA"},
    "Left Corner 3":    {"x": -220, "y": 50,   "label": "LC3"},
    "Right Corner 3":   {"x": 220,  "y": 50,   "label": "RC3"},
    "Left Wing 3":      {"x": -195, "y": 160,  "label": "LW3"},
    "Right Wing 3":     {"x": 195,  "y": 160,  "label": "RW3"},
    "Top of Key 3":     {"x": 0,    "y": 250,  "label": "TOK3"},
    "Left Mid Range":   {"x": -145, "y": 110,  "label": "LMR"},
    "Right Mid Range":  {"x": 145,  "y": 110,  "label": "RMR"},
    "Mid Range Centre": {"x": 0,    "y": 150,  "label": "MRC"},
}
 
def draw_court(ax, color="black", lw=2):
    """Draw a half basketball court."""
    # Hoop
    hoop = Circle((0, 0), radius=7.5, linewidth=lw, color=color, fill=False)
    # Backboard
    backboard = patches.Rectangle((-30, -7.5), 60, -1, linewidth=lw, color=color)
    # Paint / key
    outer_box = patches.Rectangle((-80, -47.5), 160, 190, linewidth=lw, color=color, fill=False)
    inner_box = patches.Rectangle((-60, -47.5), 120, 190, linewidth=lw, color=color, fill=False)
    # Free throw top arc
    top_free_throw = Arc((0, 142.5), 120, 120, theta1=0, theta2=180,
                          linewidth=lw, color=color, fill=False)
    # Free throw bottom arc (dashed)
    bottom_free_throw = Arc((0, 142.5), 120, 120, theta1=180, theta2=0,
                             linewidth=lw, color=color, linestyle='dashed', fill=False)
    # Restricted area arc
    restricted = Arc((0, 0), 80, 80, theta1=0, theta2=180,
                      linewidth=lw, color=color)
    # Three point line
    corner_three_a = patches.Rectangle((-220, -47.5), 0, 140,
                                        linewidth=lw, color=color)
    corner_three_b = patches.Rectangle((220, -47.5), 0, 140,
                                        linewidth=lw, color=color)
    three_arc = Arc((0, 0), 475, 475, theta1=22, theta2=158,
                    linewidth=lw, color=color)
    # Centre circle
    centre_outer = Arc((0, 422.5), 120, 120, theta1=180, theta2=0,
                        linewidth=lw, color=color)
    # Baseline
    baseline = patches.Rectangle((-250, -47.5), 500, 0, linewidth=lw, color=color)
 
    court_elements = [
        hoop, backboard, outer_box, inner_box, top_free_throw,
        bottom_free_throw, restricted, corner_three_a, corner_three_b,
        three_arc, centre_outer, baseline,
    ]
    for element in court_elements:
        ax.add_patch(element)
    return ax
 
def get_zone_color(fg_pct, attempts):
    """Return colour based on FG% — red cold, yellow average, green hot."""
    if attempts == 0:
        return "#CCCCCC", "#666666"  # grey fill, dark text
    if fg_pct >= 55:
        return "#1D9E75", "white"
    elif fg_pct >= 45:
        return "#A8D5C2", "#1a1a1a"
    elif fg_pct >= 35:
        return "#E8C97A", "#1a1a1a"
    else:
        return "#BA7517", "white"
 
def draw_zone_chart(zone_summary_dict, title):
    """Draw the full court zone chart."""
    fig, ax = plt.subplots(figsize=(8, 7.5))
    fig.patch.set_facecolor('#F5F0E8')
    ax.set_facecolor('#F5F0E8')
 
    draw_court(ax, color='#8B7355', lw=1.5)
 
    # Zone polygons — approximate boundaries
    zone_polygons = {
        "Restricted Area": plt.Polygon(
            [(-80, -47.5), (80, -47.5), (80, 40), (40, 70), (0, 80),
             (-40, 70), (-80, 40)], closed=True),
        "Left Corner 3": plt.Polygon(
            [(-250, -47.5), (-220, -47.5), (-220, 92.5), (-250, 92.5)], closed=True),
        "Right Corner 3": plt.Polygon(
            [(220, -47.5), (250, -47.5), (250, 92.5), (220, 92.5)], closed=True),
        "Left Mid Range": plt.Polygon(
            [(-220, 92.5), (-80, 92.5), (-80, -47.5), (-80, 40),
             (-80, 142.5), (-170, 142.5), (-220, 142.5)], closed=True),
        "Right Mid Range": plt.Polygon(
            [(80, -47.5), (220, -47.5), (220, 142.5), (170, 142.5),
             (80, 142.5), (80, 40)], closed=True),
        "Mid Range Centre": plt.Polygon(
            [(-80, 40), (80, 40), (80, 142.5), (-80, 142.5)], closed=True),
        "Left Wing 3": plt.Polygon(
            [(-250, 92.5), (-220, 92.5), (-220, 142.5), (-170, 142.5),
             (-135, 210), (-160, 250), (-250, 250)], closed=True),
        "Right Wing 3": plt.Polygon(
            [(220, 92.5), (250, 92.5), (250, 250), (160, 250),
             (135, 210), (170, 142.5), (220, 142.5)], closed=True),
        "Top of Key 3": plt.Polygon(
            [(-160, 250), (-135, 210), (-80, 180), (0, 170),
             (80, 180), (135, 210), (160, 250), (0, 280)], closed=True),
    }
 
    for zone_name, polygon in zone_polygons.items():
        data = zone_summary_dict.get(zone_name, {"attempts": 0, "made": 0, "fg_pct": 0})
        fill_color, text_color = get_zone_color(data["fg_pct"], data["attempts"])
 
        polygon.set_facecolor(fill_color)
        polygon.set_edgecolor('#8B7355')
        polygon.set_linewidth(1.2)
        polygon.set_alpha(0.85)
        ax.add_patch(polygon)
 
        # Label position
        cx = ZONE_DEFS[zone_name]["x"]
        cy = ZONE_DEFS[zone_name]["y"]
 
        if data["attempts"] > 0:
            ax.text(cx, cy + 10, f"{data['fg_pct']:.0f}%",
                    ha='center', va='center', fontsize=11,
                    fontweight='bold', color=text_color)
            ax.text(cx, cy - 12, f"{data['made']}/{data['attempts']}",
                    ha='center', va='center', fontsize=8, color=text_color)
        else:
            ax.text(cx, cy, "—",
                    ha='center', va='center', fontsize=11, color='#999999')
 
    # Legend
    legend_items = [
        (patches.Patch(color='#1D9E75'), 'Hot  55%+'),
        (patches.Patch(color='#A8D5C2'), 'Good  45–54%'),
        (patches.Patch(color='#E8C97A'), 'Below avg  35–44%'),
        (patches.Patch(color='#BA7517'), 'Cold  <35%'),
        (patches.Patch(color='#CCCCCC'), 'No data'),
    ]
    ax.legend(
        *zip(*legend_items),
        loc='lower right', fontsize=8,
        framealpha=0.9, frameon=True,
    )
 
    ax.set_xlim(-250, 250)
    ax.set_ylim(-50, 320)
    ax.set_title(title, fontsize=13, fontweight='bold', pad=12, color='#1a1a1a')
    ax.axis('off')
    plt.tight_layout()
    return fig
 
 
# ── Main zone chart logic ─────────────────────────────────────────────────────
if os.path.exists(SHOT_FILE):
    shot_df = pd.read_csv(SHOT_FILE)
 
    zone_view = st.radio("View", ["Individual", "Full squad"], horizontal=True)
 
    if zone_view == "Individual":
        zone_data  = shot_df[shot_df["Player"] == selected_player]
        chart_title = f"{selected_player} — Shot zones"
    else:
        zone_data  = shot_df.copy()
        chart_title = "Full squad — Shot zones"
 
    if not zone_data.empty:
        # Build zone summary dict
        zone_summary_raw = (
            zone_data.groupby("Zone")
            .agg(attempts=("Made", "count"), made=("Made", "sum"))
            .reset_index()
        )
        zone_summary_raw["fg_pct"] = (
            zone_summary_raw["made"] / zone_summary_raw["attempts"] * 100
        ).round(1)
 
        zone_dict = {
            row["Zone"]: {
                "attempts": row["attempts"],
                "made":     row["made"],
                "fg_pct":   row["fg_pct"],
            }
            for _, row in zone_summary_raw.iterrows()
        }
 
        fig = draw_zone_chart(zone_dict, chart_title)
        st.pyplot(fig)
        plt.close(fig)
 
        # Raw numbers table below chart
        with st.expander("See raw zone numbers"):
            display = zone_summary_raw.rename(columns={
                "Zone": "Zone", "attempts": "Attempts",
                "made": "Made", "fg_pct": "FG%"
            })
            st.dataframe(display, hide_index=True, use_container_width=True)
    else:
        st.info("No shot data yet — log shots using the Shot Logger page.")
else:
    st.info("No shot data yet — run shot_logger.py to start logging.")