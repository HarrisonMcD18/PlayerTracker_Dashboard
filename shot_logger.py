import streamlit as st
import pandas as pd
import os
from datetime import date
 
st.set_page_config(page_title="Shot Logger", layout="wide")
st.title("Shot Logger")
st.caption("Click a zone, log the result. One click per shot.")
 
# ── Constants ───────────────────────────────────────────────────────────────
SHOT_FILE = "data/shot_data.csv"
ZONES = [
    "Restricted Area",
    "Left Corner 3",
    "Right Corner 3",
    "Left Wing 3",
    "Right Wing 3",
    "Top of Key 3",
    "Left Mid Range",
    "Right Mid Range",
    "Mid Range Centre",
]
 
# ── Load or create shot data ─────────────────────────────────────────────────
def load_shots():
    if os.path.exists(SHOT_FILE):
        return pd.read_csv(SHOT_FILE)
    return pd.DataFrame(columns=["Date", "Player", "Opponent", "Quarter", "Zone", "Made"])
 
def save_shot(player, opponent, quarter, zone, made):
    df = load_shots()
    new_row = pd.DataFrame([{
        "Date":     str(date.today()),
        "Player":   player,
        "Opponent": opponent,
        "Quarter":  quarter,
        "Zone":     zone,
        "Made":     int(made),
    }])
    df = pd.concat([df, new_row], ignore_index=True)
    df.to_csv(SHOT_FILE, index=False)
 
# ── Sidebar — game context ───────────────────────────────────────────────────
st.sidebar.header("Game context")
 
players = [
    "Marcus Thompson", "Jordan Ellis", "Kai Okafor", "Devon Price", "Sam Nwosu"
]
opponents = [
    "Bristol Flyers", "Leicester Riders", "Cheshire Phoenix",
    "Sheffield Sharks", "London Lions"
]
 
selected_player   = st.sidebar.selectbox("Player shooting", players)
selected_opponent = st.sidebar.selectbox("Opponent", opponents)
selected_quarter  = st.sidebar.selectbox("Quarter", ["Q1", "Q2", "Q3", "Q4", "OT"])
 
st.sidebar.divider()
st.sidebar.markdown("**How to log a shot:**")
st.sidebar.markdown("1. Set player, opponent, quarter\n2. Click the zone on the court\n3. Hit Made or Missed")
st.sidebar.markdown("Logs save instantly to `shot_data.csv`")
 
# ── Zone selector — interactive court ───────────────────────────────────────
st.subheader("Select zone")
 
# Track selected zone in session state
if "selected_zone" not in st.session_state:
    st.session_state.selected_zone = None
if "last_logged" not in st.session_state:
    st.session_state.last_logged = None
 
# Zone buttons laid out to mirror court geography
st.markdown("**Corner 3s & Wings**")
col_lc3, col_lw3, col_tok3, col_rw3, col_rc3 = st.columns(5)
with col_lc3:
    if st.button("Left\nCorner 3", use_container_width=True):
        st.session_state.selected_zone = "Left Corner 3"
with col_lw3:
    if st.button("Left\nWing 3", use_container_width=True):
        st.session_state.selected_zone = "Left Wing 3"
with col_tok3:
    if st.button("Top of\nKey 3", use_container_width=True):
        st.session_state.selected_zone = "Top of Key 3"
with col_rw3:
    if st.button("Right\nWing 3", use_container_width=True):
        st.session_state.selected_zone = "Right Wing 3"
with col_rc3:
    if st.button("Right\nCorner 3", use_container_width=True):
        st.session_state.selected_zone = "Right Corner 3"
 
st.markdown("**Mid range**")
col_lmr, col_mrc, col_rmr = st.columns(3)
with col_lmr:
    if st.button("Left\nMid Range", use_container_width=True):
        st.session_state.selected_zone = "Left Mid Range"
with col_mrc:
    if st.button("Mid Range\nCentre", use_container_width=True):
        st.session_state.selected_zone = "Mid Range Centre"
with col_rmr:
    if st.button("Right\nMid Range", use_container_width=True):
        st.session_state.selected_zone = "Right Mid Range"
 
st.markdown("**Paint**")
col_blank1, col_ra, col_blank2 = st.columns([1, 1, 1])
with col_ra:
    if st.button("Restricted\nArea", use_container_width=True):
        st.session_state.selected_zone = "Restricted Area"
 
# ── Result logger ────────────────────────────────────────────────────────────
st.divider()
 
if st.session_state.selected_zone:
    st.subheader(f"Zone selected: {st.session_state.selected_zone}")
    st.markdown(f"**{selected_player}** vs {selected_opponent} — {selected_quarter}")
 
    col_made, col_missed, col_cancel = st.columns([1, 1, 2])
 
    with col_made:
        if st.button("✅ Made", use_container_width=True, type="primary"):
            save_shot(selected_player, selected_opponent, selected_quarter,
                      st.session_state.selected_zone, True)
            st.session_state.last_logged = f"✅ Made — {st.session_state.selected_zone}"
            st.session_state.selected_zone = None
            st.rerun()
 
    with col_missed:
        if st.button("❌ Missed", use_container_width=True):
            save_shot(selected_player, selected_opponent, selected_quarter,
                      st.session_state.selected_zone, False)
            st.session_state.last_logged = f"❌ Missed — {st.session_state.selected_zone}"
            st.session_state.selected_zone = None
            st.rerun()
 
    with col_cancel:
        if st.button("Cancel", use_container_width=True):
            st.session_state.selected_zone = None
            st.rerun()
else:
    st.info("Select a zone above to log a shot.")
 
# Confirmation of last logged shot
if st.session_state.last_logged:
    st.success(f"Logged: {st.session_state.last_logged}")
 
# ── Live session log ─────────────────────────────────────────────────────────
st.divider()
st.subheader("This session")
 
shots = load_shots()
if not shots.empty:
    today = str(date.today())
    session = shots[
        (shots["Player"]   == selected_player) &
        (shots["Opponent"] == selected_opponent) &
        (shots["Date"]     == today)
    ].copy()
 
    if not session.empty:
        session["Result"] = session["Made"].map({1: "✅ Made", 0: "❌ Missed"})
        st.dataframe(
            session[["Quarter", "Zone", "Result"]].reset_index(drop=True),
            use_container_width=True,
            hide_index=True,
        )
 
        total   = len(session)
        made    = session["Made"].sum()
        pct     = (made / total * 100) if total > 0 else 0
 
        m1, m2, m3 = st.columns(3)
        m1.metric("Attempts", total)
        m2.metric("Made",     int(made))
        m3.metric("FG%",      f"{pct:.1f}%")
    else:
        st.caption("No shots logged for this player/opponent today yet.")
else:
    st.caption("No shot data yet — start logging above.")
 
# ── Undo last shot ────────────────────────────────────────────────────────────
st.divider()
if st.button("↩ Undo last shot"):
    shots = load_shots()
    if not shots.empty:
        shots = shots.iloc[:-1]
        shots.to_csv(SHOT_FILE, index=False)
        st.session_state.last_logged = None
        st.success("Last shot removed.")
        st.rerun()
    else:
        st.warning("No shots to undo.")