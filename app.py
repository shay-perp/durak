import streamlit as st
import requests
import pandas as pd
import matplotlib.pyplot as plt

# כתובת ה-API
API_URL = "http://localhost:5000"

# יצירת תפריט ניווט
st.set_page_config(page_title="דוראק - ניהול משחקים", layout="wide")
st.sidebar.title("🎮 ניווט")
page = st.sidebar.radio("בחר עמוד:", ["משחק", "סטטיסטיקה"])

# --- משתנים קבועים למניעת קריסות ---
if "selected_players" not in st.session_state:
    st.session_state.selected_players = []

selected_players = st.session_state.selected_players

# --- דף המשחק ---
if page == "משחק":
    st.title("🎲 ניהול משחקים")
    st.markdown("בחר משתתפים, נהל סיבובים והזנת תוצאות.")

    # **חלק 1: הוספת שחקן חדש**
    st.header("➕ הוספת שחקן חדש")
    new_player_name = st.text_input("שם השחקן:")
    if st.button("✅ הוסף שחקן"):
        if new_player_name:
            response = requests.post(f"{API_URL}/players", json={"name": new_player_name})
            if response.status_code == 201:
                st.success(f"שחקן {new_player_name} נוסף בהצלחה!")
            else:
                st.error("⚠ שגיאה בהוספת השחקן.")

    # **חלק 2: בדיקה האם יש שחקנים במערכת**
    st.header("🏠 יצירת ערב משחק חדש")
    players_response = requests.get(f"{API_URL}/players")

    if players_response.status_code == 200:
        players = players_response.json()
        if not players:  # אם אין שחקנים כלל
            st.warning("⚠ אין שחקנים רשומים! יש להוסיף שחקנים לפני יצירת ערב משחק.")
        else:
            selected_players = st.multiselect("בחר שחקנים לערב", [p["name"] for p in players])

            # שמירת הנתונים ב-Session State
            st.session_state.selected_players = selected_players

            # הצגת המשתתפים שנבחרו
            if selected_players:
                st.subheader("🎭 שחקנים שנבחרו לערב:")
                for player in selected_players:
                    st.write(f"✔ {player}")

            if st.button("🎲 התחל ערב משחק"):
                if selected_players:
                    player_ids = [p["id"] for p in players if p["name"] in selected_players]
                    response = requests.post(f"{API_URL}/game_night/select_players", json={"players": player_ids})
                    if response.status_code == 201:
                        st.success("ערב המשחק החל!")
                    else:
                        st.error("⚠ שגיאה בהתחלת המשחק")
                else:
                    st.error("⚠ יש לבחור שחקנים!")

    else:
        st.error("❌ שגיאה בקבלת נתונים מהשרת.")

    # **חלק 3: הזנת תוצאות לכל סיבוב**
    st.header("🏆 הוספת תוצאות סיבוב")
    round_id = st.text_input("מספר סיבוב")

    scores = {}
    if selected_players:
        for player in selected_players:
            scores[player] = st.number_input(f"ניקוד של {player}", min_value=0, max_value=5)

    if st.button("✔ שמור תוצאות"):
        if round_id and scores:
            response = requests.post(f"{API_URL}/round/submit_scores", json={"round_id": round_id, "scores": scores})
            if response.status_code == 201:
                st.success("התוצאות נשמרו בהצלחה!")
            else:
                st.error("⚠ שגיאה בשמירת התוצאות")
        else:
            st.error("⚠ יש להזין מספר סיבוב ולבחור שחקנים")

# --- דף הסטטיסטיקה ---
elif page == "סטטיסטיקה":
    st.title("📊 סטטיסטיקות הפסדים")
    st.markdown("מעקב אחר הפסדים, דירוגים, וגרפים.")

    if st.button("📈 הצג סטטיסטיקות"):
        stats_response = requests.get(f"{API_URL}/stats")
        if stats_response.status_code == 200:
            stats = stats_response.json()
            if stats:
                df = pd.DataFrame(stats)

                # גרף עמודות
                fig, ax = plt.subplots()
                ax.barh(df["name"], df["losses"], color="red")
                ax.set_xlabel("כמות הפסדים")
                ax.set_ylabel("שחקנים")
                ax.set_title("השחקנים שהפסידו הכי הרבה")
                st.pyplot(fig)

                # גרף עוגה
                fig2, ax2 = plt.subplots()
                ax2.pie(df["losses"], labels=df["name"], autopct='%1.1f%%', startangle=90,
                        colors=["red", "blue", "green", "yellow"])
                ax2.set_title("אחוזי הפסדים")
                st.pyplot(fig2)
            else:
                st.write("🚨 אין עדיין נתונים.")
        else:
            st.error("⚠ שגיאה בקבלת נתונים מהשרת")
