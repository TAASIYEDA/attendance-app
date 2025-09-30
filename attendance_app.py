import streamlit as st
import pandas as pd
import os
from datetime import datetime
import gspread
from google.oauth2.service_account import Credentials

# ===== הגדרות ראשוניות =====
st.set_page_config(page_title="מערכת נוכחות תעשיידע", page_icon="🕒", layout="centered")

# ===== קבצים מקומיים =====
USERS_FILE = "מדריכים ומספר עובד.xlsx"
AUTHORITIES_FILE = "רשויות.xlsx"
PROGRAMS_FILE = "רשימת תוכניות.xlsx"

# ===== חיבור לגוגל שיטס =====
SHEET_NAME = "נוכחות תעשיידע"   # השם של ה־Google Sheet שלך
creds = Credentials.from_service_account_file(
    "credentials.json",
    scopes=["https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive"]
)
client = gspread.authorize(creds)
sheet = client.open(SHEET_NAME).sheet1

# ===== CSS לעיצוב =====
st.markdown("""
<style>
body {
    background: linear-gradient(135deg, #0f172a, #1e293b);
    font-family: 'Rubik', sans-serif;
    direction: rtl;
    color: white;
}
h1, h2, h3 {
    text-align: center;
    color: #38bdf8;
    font-weight: bold;
}
.login-card {
    max-width: 550px;
    margin: 30px auto;
    background: rgba(255, 255, 255, 0.06);
    padding: 2em;
    border-radius: 20px;
    box-shadow: 0 8px 25px rgba(0,0,0,0.7);
    text-align: center;
    backdrop-filter: blur(10px);
    border: 1px solid rgba(56, 189, 248, 0.4);
}
</style>
""", unsafe_allow_html=True)

# ===== טעינת קבצי עזר =====
if os.path.exists(USERS_FILE):
    users_df = pd.read_excel(USERS_FILE)
else:
    users_df = pd.DataFrame(columns=["מספר עובד", "שם עובד", "PIN"])

if os.path.exists(AUTHORITIES_FILE):
    authorities_df = pd.read_excel(AUTHORITIES_FILE)
    authorities = authorities_df.iloc[:,0].dropna().astype(str).tolist()
else:
    authorities = []

if os.path.exists(PROGRAMS_FILE):
    programs_df = pd.read_excel(PROGRAMS_FILE)
    programs = programs_df.iloc[:,0].dropna().astype(str).tolist()
else:
    programs = []

# ===== פונקציה לשמירת נוכחות =====
def save_attendance(emp_id, emp_name, start, end, hours, activity, authority, location, program, meeting_num, km, notes):
    sheet.append_row([
        emp_id,
        emp_name,
        datetime.now().strftime("%Y-%m-%d"),  # תאריך
        start,
        end,
        hours,
        activity,
        authority,
        location,
        program,
        meeting_num,
        km,
        notes
    ])

# ===== ממשק התחברות =====
st.markdown("<h1>📋 מערכת נוכחות תעשיידע</h1>", unsafe_allow_html=True)
st.markdown('<div class="login-card">', unsafe_allow_html=True)
st.markdown("<h3>כניסה עם מספר עובד + PIN</h3>", unsafe_allow_html=True)

emp_id = st.text_input("מס׳ עובד", max_chars=10, placeholder="הכנס מספר עובד")
pin = st.text_input("קוד PIN", type="password", max_chars=6, placeholder="****")

if st.button("כניסה"):
    if emp_id and pin:
        row = users_df[(users_df["מספר עובד"].astype(str) == emp_id) &
                       (users_df["PIN"].astype(str) == pin)]
        if not row.empty:
            emp_name = row.iloc[0]["שם עובד"]
            st.success(f"✅ שלום {emp_name}, התחברת בהצלחה!")

            # ===== טופס נוכחות =====
            with st.form("attendance_form"):
                start = st.time_input("שעת התחלה", datetime.now().time())
                end = st.time_input("שעת סיום")
                
                # חישוב שעות
                try:
                    start_dt = datetime.combine(datetime.today(), start)
                    end_dt = datetime.combine(datetime.today(), end)
                    diff = (end_dt - start_dt).seconds / 3600
                except:
                    diff = 0
                hours = round(diff, 2)

                activity = st.selectbox("סוג פעילות", ["סדנה", "מפגש", "נסיעה", "אחר"])
                authority = st.selectbox("רשות", authorities)
                location = st.text_input("מיקום")
                program = st.selectbox("תוכנית", programs)
                meeting_num = st.number_input("מס׳ מפגש", min_value=1, step=1)
                km = st.number_input("ק״מ", min_value=0, step=1)
                notes = st.text_area("הערות")

                submitted = st.form_submit_button("רישום נוכחות")
                if submitted:
                    save_attendance(emp_id, emp_name, str(start), str(end), hours, activity,
                                    authority, location, program, meeting_num, km, notes)
                    st.success("📝 הנוכחות נרשמה בהצלחה!")
        else:
            st.error("❌ מספר עובד או קוד PIN שגויים")
    else:
        st.warning("אנא מלא את כל השדות")

st.markdown('</div>', unsafe_allow_html=True)
