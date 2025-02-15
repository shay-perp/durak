import streamlit as st
import requests
import pandas as pd

API_URL = "https://your-api-url.com"

st.title("ניהול משחקים עם חברים 🎲")

# **הוספת שחקן**
st.header("📌 ניהול שחקנים")
name = st.text_input("הוסף שחקן חדש:")
if st.button("➕ הוסף שחקן"):
    if name:
        requests.post(f"{API_URL}/players", json={"name": name})
        st.success(f"שחקן {name} נוסף בהצלחה!")

# **רשימת שחקנים**
st.subheader("🎭 רשימת שחקנים:")
players = requests.get(f"{API_URL}/players").json()
player_df = pd.DataFrame(players)
st.dataframe(player_df)

# **יצירת ערב משחק**
st.header("🎲 יצירת ערב משחק")
host = st.selectbox("בחר מארח:", [p["name"] for p in players])
if st.button("🏠 התחל ערב משחק"):
    host_id = next(p["id"] for p in players if p["name"] == host)
    requests.post(f"{API_URL}/game_night", json={"host_id": host_id})
    st.success("ערב המשחק החל!")

# **הוספת סיבוב**
st.header("🏆 הוספת סיבוב")
round_name = st.text_input("שם הסיבוב:")
winner = st.selectbox("בחר מנצח:", [p["name"] for p in players])
if st.button("✔ הוסף סיבוב"):
    winner_id = next(p["id"] for p in players if p["name"] == winner)
    requests.post(f"{API_URL}/round", json={"name": round_name, "winner_id": winner_id})
    st.success("הסיבוב נוסף בהצלחה!")

# **סטטיסטיקות הפסדים**
st.header("📊 סטטיסטיקות הפסדים")
if st.button("📈 הצג סטטיסטיקות"):
    stats = requests.get(f"{API_URL}/stats").json()
    stats_df = pd.DataFrame(stats)
    st.dataframe(stats_df)
