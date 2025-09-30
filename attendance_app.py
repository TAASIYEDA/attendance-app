import streamlit as st
import pandas as pd
import os
from datetime import datetime

# ===== הגדרות ראשוניות =====
st.set_page_config(page_title="מערכת נוכחות תעשיידע", page_icon="🕒", layout="centered")

DATA_FILE = "attendance_data.xlsx"
USERS_FILE = "מדריכים ומספר עובד.xlsx"

# ===== CSS לעיצוב =====
st.markdown("""
<style>
/* רקע כללי כהה טכנולוגי */
body {
    background: linear-gradient(135deg, #0f172a, #1e293b);
    font-family: 'Rubik', sans-serif;
    direction: rtl;
    color: white;
}

/* כותרות */
h1, h2, h3 {
    text-align: center;
    color: #38bdf8;
    font-weight: bold;
}

/* כרטיס כניסה */
.login-card {
    max-width: 400px;
    margin: 80px auto;
    background: rgba(255, 255, 255, 0.06);
    padding: 2em;
    border-radius: 20px;
    box-shadow: 0 8px 25px rgba(0,0,0,0.7);
    text-align: center;
    backdrop-filter: blur(10px);
    border: 1px solid rgba(56, 189, 248, 0.4);
}

/* תיבות קלט קטנות */
div[data-testid="stTextInput"] {
    max-width: 150px;
    margin: 10px auto;
}
div[data-testid="stTextInput"] input {
    text-align: center;
    font-size: 1.1em;
    border-radius: 10px;
    padding: 0.5em;
    background-color: rgba(255,255,255,0.1);
    border: 1px solid rgba(56, 189, 248, 0.6);
    color: white;
}

/* כפתור */
.stButton>button {
    width: 100%;
    padding: 0.9em;
    border-radius: 30px;
    border: none;
    background: linear-gradient(90deg, #3b82f6, #06b6d4);
    color: white;
    font-weight: bold;
    font-size: 1.1em;
    transition: 0.3s ease;
    cursor: pointer;
}
.stButton>button:hover {
    transform: translateY(-3px);
    background: linear-gradient(90deg, #06b6d4, #3b82f6);
    box-shadow: 0 0 15px rgba(56, 189, 248, 0.6);
}

/* הסתרת שדות ריקים (כדי שלא יהיה ריבוע לבן) */
div[data-testid="stTextInput"]:has(label:empty) {
    display: none !important;
}
</style>
""", unsafe_allow_html=True)

# ===== טעינת משתמשים =====
if os.path.exists(USERS_FILE):
    users_df = pd.read_excel(USERS_FILE)
else:
    users_df = pd.DataFrame(columns=["מספר עובד", "שם", "PIN"])

# ===== פונקציה לשמירת נוכחות =====
def save_attendance(emp_id, emp_name):
    new_entry = {
        "מספר עובד": emp_id,
        "שם": emp_name,
        "תאריך": datetime.now().strftime("%Y-%m-%d"),
        "שעה": datetime.now().strftime("%H:%M:%S")
    }

    if os.path.exists(DATA_FILE):
        df = pd.read_excel(DATA_FILE)
    else:
        df = pd.DataFrame(columns=new_entry.keys())

    df = pd.concat([df, pd.DataFrame([new_entry])], ignore_index=True)
    df.to_excel(DATA_FILE, index=False)

# ===== ממשק התחברות =====
st.markdown("<h1>📋 מערכת נוכחות תעשיידע</h1>", unsafe_allow_html=True)

st.markdown('<div class="login-card">', unsafe_allow_html=True)
st.markdown("<h3>כניסה עם מספר עובד + PIN</h3>", unsafe_allow_html=True)

# שדות עם מגבלת 4 ספרות
emp_id = st.text_input("מספר עובד", max_chars=4, placeholder="____")
pin = st.text_input("קוד PIN", type="password", max_chars=4, placeholder="****")

if st.button("כניסה"):
    if emp_id and pin:
        row = users_df[(users_df["מספר עובד"].astype(str) == emp_id) &
                       (users_df["PIN"].astype(str) == pin)]
        if not row.empty:
            emp_name = row.iloc[0]["שם"]
            save_attendance(emp_id, emp_name)
            st.success(f"✅ שלום {emp_name}, הנוכחות נרשמה בהצלחה!")
        else:
            st.error("❌ מספר עובד או קוד PIN שגויים")
    else:
        st.warning("אנא מלא את כל השדות")

st.markdown('</div>', unsafe_allow_html=True)

# ===== הצגת דוח למנהל בלבד =====
st.markdown("---")
st.subheader("📊 דוח נוכחות (למנהל בלבד)")

if os.path.exists(DATA_FILE):
    df = pd.read_excel(DATA_FILE)
    st.dataframe(df, use_container_width=True)
else:
    st.info("עדיין לא נרשמו נוכחויות.")
