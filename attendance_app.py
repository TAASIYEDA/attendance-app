import streamlit as st
import pandas as pd
import os
from datetime import datetime

# ==================================
# ==== [SYSTEM_CONFIG] ====
# ==================================

st.set_page_config(page_title="מערכת נוכחות תעשיידע", page_icon="🕒", layout="centered")

DATA_FILE = "attendance_data.xlsx"
USERS_FILE = "מדריכים ומספר עובד.xlsx"

# ==================================
# ==== [UI_INJECTION_MODULE: CYBERPUNK] ====
# ==================================

st.markdown("""
<style>
/* 1. רקע: כהה מאוד עם אפקט Matrix עדין */
body {
    background: #000000; /* שחור מוחלט */
    font-family: 'Consolas', 'Courier New', monospace; /* פונט טכנולוגי */
    direction: rtl;
    color: #00ff7f; /* ירוק בהיר - צבע Matrix */
}

/* 2. כותרות: זוהר ניאון כחול */
h1, h2, h3 {
    text-align: center;
    color: #00ffff; /* ציאן/כחול ניאון */
    font-weight: bold;
    text-shadow: 0 0 10px rgba(0, 255, 255, 0.7); /* אפקט זוהר */
}

/* 3. כרטיס כניסה: פאנל שקוף וזוהר */
.login-card {
    max-width: 400px;
    margin: 80px auto;
    background: rgba(0, 0, 0, 0.7); /* שחור שקוף יותר */
    padding: 2.5em;
    border-radius: 5px;
    box-shadow: 0 0 25px rgba(0, 255, 255, 0.6), 0 0 5px rgba(0, 255, 255, 0.4); /* זוהר ניאון חזק */
    text-align: center;
    backdrop-filter: blur(4px);
    border: 1px solid #00ffff;
}

/* 4. תיבות קלט: ממשק מסוף (Console Input) */
div[data-testid="stTextInput"] {
    max-width: 180px;
    margin: 15px auto;
}
div[data-testid="stTextInput"] input {
    text-align: center;
    font-size: 1.2em;
    border-radius: 0; /* קווים ישרים */
    padding: 0.6em;
    background-color: #000000;
    border: 1px solid #00ff7f; /* ירוק זוהר */
    color: #00ff7f;
    box-shadow: 0 0 5px #00ff7f;
}

/* 5. כפתור: כפתור לחימה (Activation Button) */
.stButton>button {
    width: 100%;
    padding: 1.1em;
    border-radius: 5px;
    border: 2px solid #00ffff;
    background: linear-gradient(90deg, #00ffff, #007bff); /* ציאן-כחול */
    color: #000000;
    font-weight: bold;
    font-size: 1.2em;
    transition: 0.2s ease;
    cursor: pointer;
    box-shadow: 0 0 15px #00ffff;
}
.stButton>button:hover {
    transform: translateY(-2px);
    background: linear-gradient(90deg, #007bff, #00ffff);
    box-shadow: 0 0 25px #00ffff, 0 0 5px #00ffff; /* זוהר משופר בלחיצה */
}

/* 6. הודעות מערכת */
div[data-testid="stAlert"] {
    border-radius: 5px;
    margin-top: 15px;
    font-weight: bold;
    font-family: 'Consolas', monospace;
}
.stSuccess { background-color: rgba(0, 255, 127, 0.1) !important; color: #00ff7f !important; border: 1px solid #00ff7f !important;} /* ירוק Matrix */
.stError { background-color: rgba(255, 0, 0, 0.1) !important; color: #ff3333 !important; border: 1px solid #ff3333 !important;} /* אדום אזהרה */
.stWarning { background-color: rgba(255, 165, 0, 0.1) !important; color: #ffa500 !important; border: 1px solid #ffa500 !important;} /* כתום אזהרה */

/* 7. טבלת דאטה (דוח): מראה מסוף נתונים */
.dataframe {
    background-color: #000000;
    color: #00ff7f;
    font-family: 'Consolas', monospace;
    border: 1px solid #00ffff;
    box-shadow: 0 0 10px rgba(0, 255, 255, 0.3);
}
.dataframe th {
    background-color: #1a1a1a;
    color: #00ffff;
    border-bottom: 2px solid #00ffff;
}
.dataframe td {
    border: none;
    padding: 8px;
}
/* הסתרת שדות ריקים */
div[data-testid="stTextInput"]:has(label:empty) {
    display: none !important;
}
</style>
""", unsafe_allow_html=True)

# ==================================
# ==== [DATA_ACCESS_LAYER] ====
# ==================================

# פונקציה לטעינת משתמשים - שימוש ב-st.cache_data לשיפור ביצועים
@st.cache_data
def load_users():
    """טוען את נתוני המשתמשים מקובץ האקסל."""
    if os.path.exists(USERS_FILE):
        # ציון types לוודא שמספר עובד ו-PIN נקראים כמחרוזות (str)
        dtype_spec = {"מספר עובד": str, "PIN": str}
        return pd.read_excel(USERS_FILE, dtype=dtype_spec)
    else:
        # יצירת DataFrame ריק אם הקובץ לא קיים
        return pd.DataFrame(columns=["מספר עובד", "שם העובד", "PIN"])

users_df = load_users()

# פונקציה לשמירת נוכחות
def save_attendance(emp_id, emp_name):
    """רושם כניסת נוכחות לקובץ הנתונים."""
    current_time = datetime.now()
    new_entry = {
        "מספר עובד": emp_id,
        "שם העובד": emp_name,
        "תאריך": current_time.strftime("%Y-%m-%d"),
        "שעה": current_time.strftime("%H:%M:%S")
    }

    if os.path.exists(DATA_FILE):
        df = pd.read_excel(DATA_FILE)
    else:
        df = pd.DataFrame(columns=new_entry.keys())

    # הוספת השורה החדשה באמצעות pd.concat
    df = pd.concat([df, pd.DataFrame([new_entry])], ignore_index=True)
    df.to_excel(DATA_FILE, index=False)

# ==================================
# ==== [MAIN_INTERFACE_MODULE] ====
# ==================================

st.markdown("<h1>📋 מערכת נוכחות תעשיידע</h1>", unsafe_allow_html=True)

st.markdown('<div class="login-card">', unsafe_allow_html=True)
st.markdown("<h3>כניסה עם מספר עובד + PIN</h3>", unsafe_allow_html=True)

# שדות קלט
emp_id = st.text_input("מספר עובד", max_chars=4, placeholder="____")
pin = st.text_input("קוד PIN", type="password", max_chars=4, placeholder="****")

if st.button("כניסה"):
    # ודא שהקלט קיים ומכיל בדיוק 4 תווים
    if emp_id and pin and len(emp_id) == 4 and len(pin) == 4:
        
        # חפש התאמה ב-DataFrame
        row = users_df[(users_df["מספר עובד"] == emp_id) & 
                       (users_df["PIN"] == pin)]
        
        if not row.empty:
            emp_name = row.iloc[0]["שם העובד"] 
            save_attendance(emp_id, emp_name)
            # הודעת הצלחה עם עיצוב טכנולוגי
            st.success(f"✅ [ACCESS GRANTED] שלום {emp_name}, הנוכחות נרשמה בהצלחה! [TIMESTAMP: {datetime.now().strftime('%H:%M:%S')}]")
        else:
            # הודעת שגיאה עם עיצוב טכנולוגי
            st.error("❌ [ACCESS DENIED] מספר עובד או קוד PIN שגויים. אנא ודא קלט.")
    else:
        # הודעת אזהרה עם עיצוב טכנולוגי
        st.warning("⚠️ [INPUT ERROR] אנא מלא את כל השדות (4 ספרות לכל שדה).")

st.markdown('</div>', unsafe_allow_html=True)

# ==================================
# ==== [ADMIN_REPORT_MODULE] ====
# ==================================

st.markdown("---")
st.subheader("📊 דוח נוכחות (למנהל בלבד) [DATA FEED]")

if os.path.exists(DATA_FILE):
    # טעינה מחדש של הנתונים העדכניים לדוח
    df = pd.read_excel(DATA_FILE)
    # סדר את הנתונים לפי תאריך ושעה יורדים
    df_sorted = df.sort_values(by=['תאריך', 'שעה'], ascending=False)
    st.dataframe(df_sorted, use_container_width=True)
else:
    st.info("⚡ [STANDBY MODE] עדיין לא נרשמו נוכחויות.")