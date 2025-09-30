import streamlit as st
import pandas as pd
import os
from datetime import datetime
from io import BytesIO

# ==================================================
# ==== [SYSTEM_CONFIG & CONSTANTS] ====
# ==================================================

# קבצי הנתונים לאחסון (כמו LocalStorage)
USERS_FILE = "users_data.xlsx"
RECORDS_FILE = "records_data.xlsx"

ROLES = { 'admin': 'Admin', 'manager': 'מנהל', 'instructor': 'מדריך' }
PROGRAMS = ['ביומימיקרי','בינה מלאכותית','רוקחים עולם','טכנולוגיות החלל','יישומי AI','פורצות דרך','מנהיגות ירוקה','השמיים אינם הגבול','ביומימיקרי לחטיבות','טכנו-כיף','תמיר','חוצה ישראל','מקורות']
MUNICIPALITIES = ['אופקים','אשדוד','אשכול','אשקלון','באר יעקב','באר שבע','חדרה','חיפה','יבנה','לכיש','מ.א חוף אשקלון','מודיעין','מטה יהודה','מסעדה','נהריה','נתניה','עין אלאסד','עין קניא (רשות)','עכו','עמק הירדן','צפון + דרום','קריית גת','ראשון לציון','רחובות','רמלה','שדות דן','שדרות','שפיר','יד בנימין','הרצליה','קריית שמונה','בנימינה','נצרת','עפולה','בית שאן','ירוחם','אחר, לציין בהערות.']
ACTIVITY_TYPES = ['הכשרה','קורסים','סדנאות','סיורים','ביטול זמן']

# משתמשי ברירת מחדל (כמו במקור ה-JS)
DEFAULT_USERS = [
    {'id': 'u1', 'name': 'עידן נחום', 'empNumber': '8500', 'pin': '2311', 'role': 'admin'},
    {'id': 'u2', 'name': 'מנהל', 'empNumber': '8501', 'pin': '2025', 'role': 'manager'},
    {'id': 'u3', 'name': 'מדריך 8502', 'empNumber': '8502', 'pin': '1212', 'role': 'instructor'},
]

# ==================================================
# ==== [STREAMLIT_CONFIG & UI_CSS_INJECTION] ====
# ==================================================

st.set_page_config(
    page_title="מערכת נוכחות תעשיידע",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# הזרקת CSS לעיצוב טכנולוגי (Neo-Grid/Cyberpunk)
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
/* כותרות משנה קטנות יותר */
.stTabs [data-testid="stCustomWrapper"] h3 {
    text-align: right;
    color: #00ff7f;
    text-shadow: none;
}

/* 3. כרטיסים (בשימוש ללוגין ולטפסים) */
.login-card {
    max-width: 450px;
    margin: 80px auto 40px;
    background: rgba(0, 0, 0, 0.7);
    padding: 2.5em;
    border-radius: 5px;
    box-shadow: 0 0 25px rgba(0, 255, 255, 0.6), 0 0 5px rgba(0, 255, 255, 0.4);
    text-align: center;
    backdrop-filter: blur(4px);
    border: 1px solid #00ffff;
}

/* 4. שדות קלט (TextField, SelectBox) */
div[data-testid="stTextInput"] input, 
div[data-testid="stDateInput"] input,
div[data-testid="stTimeInput"] input,
div[data-testid="stNumberInput"] input,
div[data-testid="stSelectbox"] div[role="combobox"] {
    font-size: 1.0em !important;
    border-radius: 0 !important; /* קווים ישרים */
    padding: 0.6em !important;
    background-color: #000000 !important;
    border: 1px solid #00ff7f !important; /* ירוק זוהר */
    color: #00ff7f !important;
    box-shadow: 0 0 5px #00ff7f !important;
}

/* 5. כפתור ראשי */
.stButton>button {
    padding: 0.8em 1.5em;
    border-radius: 5px;
    border: 2px solid #00ffff;
    background: linear-gradient(90deg, #00ffff, #007bff); /* ציאן-כחול */
    color: #000000;
    font-weight: bold;
    font-size: 1.1em;
    transition: 0.2s ease;
    cursor: pointer;
    box-shadow: 0 0 10px #00ffff;
}
.stButton>button:hover {
    transform: translateY(-1px);
    background: linear-gradient(90deg, #007bff, #00ffff);
    box-shadow: 0 0 20px #00ffff, 0 0 5px #00ffff; /* זוהר משופר */
}

/* 6. כפתורים משניים (Secondary) */
.stButton:has(button[kind="secondary"]) button {
    background: #1a1a1a;
    color: #00ff7f;
    border: 1px solid #00ff7f;
    box-shadow: 0 0 5px #00ff7f;
}

/* 7. דאטה פריים (טבלה) - מראה מסוף נתונים */
.dataframe {
    background-color: #000000;
    color: #00ff7f;
    font-family: 'Consolas', monospace;
    border: 1px solid #00ffff;
    box-shadow: 0 0 10px rgba(0, 255, 255, 0.3);
}
.stDataFrame {
    direction: ltr !important; /* יישור נתונים למרכז/שמאל בטבלה */
}

/* 8. התראות (Warnings/Success) */
.stAlert {
    border-radius: 5px;
    font-weight: bold;
    font-family: 'Consolas', monospace;
}
.stSuccess { background-color: rgba(0, 255, 127, 0.1) !important; color: #00ff7f !important; border: 1px solid #00ff7f !important;} /* ירוק Matrix */
.stError { background-color: rgba(255, 0, 0, 0.1) !important; color: #ff3333 !important; border: 1px solid #ff3333 !important;} /* אדום אזהרה */
.stWarning { background-color: rgba(255, 165, 0, 0.1) !important; color: #ffa500 !important; border: 1px solid #ffa500 !important;} /* כתום אזהרה */
</style>
""", unsafe_allow_html=True)


# ==================================================
# ==== [HELPER_FUNCTIONS] ====
# ==================================================

def calc_hours(start_time, end_time):
    """מחשב הפרש שעות בין שני אובייקטי datetime.time ומחזיר מחרוזת HH:MM."""
    if not start_time or not end_time:
        return ""
    try:
        start_dt = datetime.combine(datetime.min.date(), start_time)
        end_dt = datetime.combine(datetime.min.date(), end_time)
        if end_dt < start_dt:
            end_dt = end_dt.replace(day=end_dt.day + 1)
        
        diff = end_dt - start_dt
        total_minutes = int(diff.total_seconds() / 60)
        
        hours = total_minutes // 60
        minutes = total_minutes % 60
        return f"{hours:02d}:{minutes:02d}"
    except Exception:
        return ""

def init_data():
    """טוען או יוצר את קבצי הנתונים."""
    if 'users_df' not in st.session_state:
        if os.path.exists(USERS_FILE):
            st.session_state.users_df = pd.read_excel(USERS_FILE, dtype={'empNumber': str, 'pin': str})
        else:
            st.session_state.users_df = pd.DataFrame(DEFAULT_USERS)
            save_data(st.session_state.users_df, USERS_FILE)

    if 'records_df' not in st.session_state:
        if os.path.exists(RECORDS_FILE):
            st.session_state.records_df = pd.read_excel(RECORDS_FILE, dtype={'empNumber': str, 'meetingNumber': 'Int64'})
        else:
            st.session_state.records_df = pd.DataFrame(columns=['id', 'empNumber', 'empName', 'date', 'start', 'end', 'hours', 'type', 'municipality', 'location', 'program', 'meetingNumber', 'km', 'notes'])
            save_data(st.session_state.records_df, RECORDS_FILE)

def save_data(df, filename):
    """שומר DataFrame לקובץ Excel."""
    try:
        df.to_excel(filename, index=False)
    except Exception as e:
        st.error(f"שגיאה בשמירת קובץ הנתונים {filename}: {e}")

def get_emp_name(emp_number):
    """מחזיר שם עובד לפי מספר עובד."""
    user = st.session_state.users_df[st.session_state.users_df['empNumber'] == emp_number]
    return user.iloc[0]['name'] if not user.empty else "שם לא ידוע"

def get_filtered_records(df, filters):
    """מחיל מסננים על טבלת הרשומות."""
    filtered_df = df.copy()

    # 1. סינון לפי תפקיד: מדריך רואה רק את הרשומות שלו
    if st.session_state.user_role == 'instructor':
        filtered_df = filtered_df[filtered_df['empNumber'] == st.session_state.emp_number]
    # 2. סינון לפי מדריך (למנהל/אדמין)
    elif filters.get('emp') and filters['emp'] != 'הכל':
        filtered_df = filtered_df[filtered_df['empNumber'] == filters['emp']]

    # 3. סינון טווח תאריכים
    if filters.get('from_date'):
        filtered_df = filtered_df[filtered_df['date'] >= filters['from_date']]
    if filters.get('to_date'):
        filtered_df = filtered_df[filtered_df['date'] <= filters['to_date']]
    
    # 4. סינון לפי סוג
    if filters.get('type') and filters['type'] != 'הכל':
        filtered_df = filtered_df[filtered_df['type'] == filters['type']]
    
    # 5. סינון לפי רשות
    if filters.get('municipality') and filters['municipality'] != 'הכל':
        filtered_df = filtered_df[filtered_df['municipality'] == filters['municipality']]

    # 6. סינון לפי תוכנית
    if filters.get('program') and filters['program'] != 'הכל':
        # רשומות ללא תוכנית נחשבות ריקות
        filtered_df = filtered_df[filtered_df['program'].fillna('') == filters['program']]

    # מיון: החדשים למעלה (כמו במקור ה-JS)
    filtered_df = filtered_df.sort_values(by=['date', 'start'], ascending=False)
    return filtered_df.reset_index(drop=True)

# ==================================================
# ==== [VIEWS] ====
# ==================================================

def login_view():
    """ממשק כניסה למערכת."""
    st.markdown('<div class="login-card">', unsafe_allow_html=True)
    st.markdown("<h2>כניסה למערכת: אימות ($ACCESS$)</h2>", unsafe_allow_html=True)

    with st.form("login_form"):
        emp_number = st.text_input("מס׳ עובד (4 ספרות)", max_chars=4)
        pin = st.text_input("קוד PIN", type="password", max_chars=4)
        
        submitted = st.form_submit_button("אימות וגישה ($COMMIT$)", use_container_width=True)

        if submitted:
            user = st.session_state.users_df[
                (st.session_state.users_df['empNumber'] == emp_number.strip()) & 
                (st.session_state.users_df['pin'] == pin.strip())
            ]
            
            if not user.empty:
                st.session_state.logged_in = True
                st.session_state.emp_number = user.iloc[0]['empNumber']
                st.session_state.user_name = user.iloc[0]['name']
                st.session_state.user_role = user.iloc[0]['role']
                st.rerun()
            else:
                st.error("❌ [ACCESS DENIED] מספר עובד או קוד PIN שגויים. אנא ודא קלט.")
    st.markdown('</div>', unsafe_allow_html=True)

def logout():
    """מנתק את המשתמש ומנקה את ה-session state."""
    st.session_state.logged_in = False
    st.session_state.emp_number = None
    st.session_state.user_name = None
    st.session_state.user_role = None
    st.session_state.current_tab = 'form'
    st.success("ניתוק בוצע בהצלחה.")
    st.rerun()

def main_app_view():
    """ממשק האפליקציה הראשי (לאחר כניסה)."""
    
    # הצגת כותרת ואזור משתמש
    col_title, col_user = st.columns([4, 1])
    with col_title:
        st.markdown("<h1>📋 מערכת נוכחות תעשיידע</h1>", unsafe_allow_html=True)
    with col_user:
        role_label = ROLES.get(st.session_state.user_role, 'אורח')
        st.markdown(f"""
            <div style="text-align: left; margin-top: 15px;">
                <div style="color:#00ffff; font-weight:bold;">{st.session_state.user_name}</div>
                <div style="color:#00ff7f; font-size:0.9em;">{role_label} • {st.session_state.emp_number}</div>
                <button onclick="window.parent.document.getElementById('logoutBtn').click();" style="
                    background: #991b1b; color: white; border: none; padding: 4px 8px; 
                    border-radius: 4px; font-size: 0.8em; margin-top: 5px; cursor: pointer;">
                    ניתוק ($LOGOUT$)
                </button>
            </div>
            """, unsafe_allow_html=True)

    # שימוש ב-st.tabs ליישום ה-Tab Bar המקורי
    tab_names = ['רישום נוכחות', 'דוחות וטבלה', 'ייצוא נתונים']
    if st.session_state.user_role in ['admin', 'manager']:
        tab_names.append('ניהול משתמשים')
    
    tabs = st.tabs(tab_names)
    
    # ----------------------------------
    # TAB 1: רישום נוכחות (Form)
    # ----------------------------------
    with tabs[0]:
        attendance_form_tab()

    # ----------------------------------
    # TAB 2: דוחות וטבלה (Table/Grid)
    # ----------------------------------
    with tabs[1]:
        data_grid_tab()

    # ----------------------------------
    # TAB 3: ייצוא נתונים (Export)
    # ----------------------------------
    with tabs[2]:
        export_tab()
    
    # ----------------------------------
    # TAB 4: ניהול משתמשים (Admin Only)
    # ----------------------------------
    if st.session_state.user_role in ['admin', 'manager']:
        with tabs[3]:
            admin_users_tab()

def attendance_form_tab():
    """טופס רישום נוכחות (Create/Update)."""
    st.subheader("טופס רישום / עדכון פעילות ($DATA\_INPUT$)")

    # משתנים לשמירת נתונים בטופס
    if 'form_data' not in st.session_state:
        st.session_state.form_data = {}
    
    # קריאה לפונקציית עדכון שעות אוטומטי
    def update_hours():
        start = st.session_state.form_data.get('start')
        end = st.session_state.form_data.get('end')
        st.session_state.form_data['hours'] = calc_hours(start, end)
    
    with st.form("attendance_form", clear_on_submit=True):
        st.markdown('<h4 style="color:#00ff7f;">זמן ומשך ($TIMESTAMP$)</h4>', unsafe_allow_html=True)
        col1, col2, col3, col4, col5 = st.columns([1, 1, 1, 1, 1])
        
        with col1:
            date = st.date_input("תאריך", value=datetime.today(), key='date_input')
        with col2:
            start_time = st.time_input("שעת התחלה", value=datetime.now(), key='start', on_change=update_hours)
        with col3:
            end_time = st.time_input("שעת סיום", value=datetime.now(), key='end', on_change=update_hours)
        with col4:
            hours = st.text_input("סה״כ שעות (מחושב)", value=st.session_state.form_data.get('hours', ''), disabled=True)
        with col5:
            meeting_number = st.number_input("מס׳ מפגש", min_value=1, step=1, key='meetingNumber_input', format='%d')

        st.markdown("---")
        st.markdown('<h4 style="color:#00ff7f;">פרטי פעילות ($ACTIVITY\_PARAMS$)</h4>', unsafe_allow_html=True)
        col6, col7, col8, col9, col10 = st.columns([1, 2, 2, 2, 1])

        with col6:
            activity_type = st.selectbox("סוג פעילות", ACTIVITY_TYPES, index=None, placeholder="בחרו...", key='type_input')
        with col7:
            municipality = st.selectbox("רשות", MUNICIPALITIES, index=None, placeholder="בחרו רשות", key='municipality_input')
        with col8:
            location = st.text_input("שם בית הספר (הקלדה)", placeholder="לדוגמה: מקיף ה׳", key='location_input')
        with col9:
            program = st.selectbox("תוכנית (קורס)", [''] + PROGRAMS, index=0, key='program_input')
        with col10:
            km = st.number_input("ק״מ (נסיעות)", min_value=0.0, step=0.1, key='km_input')

        notes = st.text_area("הערות", key='notes_input')

        submitted = st.form_submit_button("שמור רשומה ($COMMIT$)", use_container_width=False)

        if submitted:
            if not all([date, start_time, end_time, activity_type, municipality, location]):
                st.error("⚠️ [INPUT ERROR] אנא מלא את כל שדות החובה.")
            else:
                new_record = {
                    'id': str(pd.Timestamp.now().value), # ייצור ID ייחודי
                    'empNumber': st.session_state.emp_number,
                    'empName': st.session_state.user_name,
                    'date': date.isoformat(),
                    'start': start_time.strftime('%H:%M'),
                    'end': end_time.strftime('%H:%M'),
                    'hours': calc_hours(start_time, end_time),
                    'type': activity_type,
                    'municipality': municipality,
                    'location': location.strip(),
                    'program': program,
                    'meetingNumber': meeting_number if meeting_number else pd.NA,
                    'km': km,
                    'notes': notes.strip(),
                }
                
                # הוספת רשומה
                df = st.session_state.records_df
                new_df = pd.DataFrame([new_record])
                st.session_state.records_df = pd.concat([df, new_df], ignore_index=True)
                save_data(st.session_state.records_df, RECORDS_FILE)
                st.success(f"✅ [ACCESS GRANTED] הרשומה נשמרה בהצלחה. סה\"כ שעות: {new_record['hours']}")
                st.session_state.form_data = {} # ניקוי נתוני השעות המחושבות
                # st.rerun() # אין צורך ב-rerun כי הטופס מתנקה אוטומטית

def data_grid_tab():
    """דוחות וטבלת סינון (Read & Filter)."""
    st.subheader("דוח נוכחות: גריד נתונים ($DATA\_GRID$)")

    # ניהול מצב המסננים
    if 'filters' not in st.session_state:
        st.session_state.filters = {}

    # יצירת המסננים ב-3 עמודות
    with st.container():
        col_f1, col_f2, col_f3 = st.columns(3)
        
        with col_f1:
            st.date_input("מתאריך", key='from_date', value=None, on_change=lambda: st.session_state.filters.update({'from_date': st.session_state.from_date}))
            st.date_input("עד תאריך", key='to_date', value=None, on_change=lambda: st.session_state.filters.update({'to_date': st.session_state.to_date}))
        
        with col_f2:
            st.selectbox("סוג פעילות", ['הכל'] + ACTIVITY_TYPES, key='type_filter', on_change=lambda: st.session_state.filters.update({'type': st.session_state.type_filter}))
            st.selectbox("רשות", ['הכל'] + MUNICIPALITIES, key='municipality_filter', on_change=lambda: st.session_state.filters.update({'municipality': st.session_state.municipality_filter}))

        with col_f3:
            st.selectbox("תוכנית", ['הכל'] + PROGRAMS, key='program_filter', on_change=lambda: st.session_state.filters.update({'program': st.session_state.program_filter}))
            
            # סינון מדריך (רק למנהל/אדמין)
            if st.session_state.user_role in ['admin', 'manager']:
                emp_list = ['הכל'] + st.session_state.users_df['empNumber'].tolist()
                st.selectbox("מדריך", emp_list, key='emp_filter', on_change=lambda: st.session_state.filters.update({'emp': st.session_state.emp_filter}))
            else:
                st.session_state.filters.pop('emp', None)

        if st.button("נקה מסננים", key='clear_filters', type='secondary'):
            st.session_state.filters = {}
            st.session_state.from_date = None
            st.session_state.to_date = None
            st.session_state.type_filter = 'הכל'
            st.session_state.municipality_filter = 'הכל'
            st.session_state.program_filter = 'הכל'
            if 'emp_filter' in st.session_state: st.session_state.emp_filter = 'הכל'
            st.rerun()

    # החלת סינון וחישוב נתונים מסוננים
    filtered_df = get_filtered_records(st.session_state.records_df, st.session_state.filters)
    
    # שמירת הנתונים המסוננים למצב ה-session לצורך ייצוא
    st.session_state.last_rendered_df = filtered_df
    
    if filtered_df.empty:
        st.info("⚡ [STANDBY MODE] לא נמצאו רשומות תואמות למסננים.")
    else:
        st.markdown("---")
        
        # חישוב סיכומים
        total_hours_str = filtered_df['hours'].str.split(':').apply(lambda x: int(x[0])*60 + int(x[1])).sum()
        total_hours_formatted = f"{int(total_hours_str // 60):02d}:{int(total_hours_str % 60):02d}"
        total_km = filtered_df['km'].sum()
        
        col_sum1, col_sum2, _ = st.columns([1, 1, 3])
        with col_sum1:
            st.markdown(f"**סה״כ שעות:** <span style='color:#00ffff; font-size:1.2em;'>{total_hours_formatted}</span>", unsafe_allow_html=True)
        with col_sum2:
            st.markdown(f"**סה״כ ק״מ:** <span style='color:#00ffff; font-size:1.2em;'>{total_km:.1f}</span>", unsafe_allow_html=True)

        # טבלת נתונים
        columns_display = ['date', 'start', 'end', 'hours', 'type', 'municipality', 'location', 'program', 'meetingNumber', 'km', 'notes']
        column_order = ['empName', 'empNumber'] + columns_display
        
        # הצגת כפתורי פעולות בכמות גדולה
        with st.expander("פעולות בכמות גדולה ($BULK\_ACTIONS$)", expanded=False):
            st.warning("⚠️ פונקציונליות מחיקה ושכפול גורפת אינה זמינה כרגע בגרסת Streamlit זו (נדרשת טבלת עריכה מורכבת).")
            # אם היינו משתמשים ב-st.experimental_data_editor היינו יכולים להוסיף פעולות אלה.

        st.dataframe(filtered_df[column_order], use_container_width=True, hide_index=True,
                     column_names={
                         'empName': 'שם עובד', 'empNumber': 'מס׳ עובד', 'date': 'תאריך', 'start': 'התחלה', 
                         'end': 'סיום', 'hours': 'שעות', 'type': 'סוג פעילות', 'municipality': 'רשות', 
                         'location': 'מיקום', 'program': 'תוכנית', 'meetingNumber': 'מס׳ מפגש', 'km': 'ק״מ', 
                         'notes': 'הערות'
                     })


def export_tab():
    """ממשק ייצוא נתונים (Export)."""
    st.subheader("ייצוא נתונים ($DATA\_EXFILTRATION$)")
    
    col_opt, col_filtered, col_monthly = st.columns(3)
    
    # --- העדפות ייצוא ---
    with col_opt:
        st.markdown('<h4 style="color:#00ff7f;">העדפות ייצוא ($OPTIONS$)</h4>', unsafe_allow_html=True)
        heb_headers = st.checkbox("כותרות עמודות בעברית", value=True)
        include_id = st.checkbox("כלול מזהה פנימי (id)", value=False)
        st.caption("אפשרויות אלה חלות על כל הייצוא.")
    
    # --- ייצוא מסונן ---
    with col_filtered:
        st.markdown('<h4 style="color:#00ff7f;">ייצוא לפי המסננים הנוכחיים ($GRID\_VIEW$)</h4>', unsafe_allow_html=True)
        
        @st.cache_data
        def to_excel(df, opts):
            """המרת DataFrame ל-Bytes (Excel) כולל עמודות סיכום וכותרות."""
            output = BytesIO()
            writer = pd.ExcelWriter(output, engine='xlsxwriter')
            
            # הכנת נתונים
            keys = ['empNumber', 'empName', 'date', 'start', 'end', 'hours', 'type', 'municipality', 'location', 'program', 'meetingNumber', 'km', 'notes']
            headers_heb = ['מס׳ עובד', 'שם עובד', 'תאריך', 'התחלה', 'סיום', 'שעות', 'סוג פעילות', 'רשות', 'מיקום', 'תוכנית', 'מס׳ מפגש', 'ק״מ', 'הערות']
            
            if opts['include_id']:
                keys.insert(0, 'id')
                headers_heb.insert(0, 'מזהה')

            df_export = df.copy()
            df_export = df_export.rename(columns=dict(zip(keys, headers_heb)))
            df_export = df_export[headers_heb] # סידור עמודות

            df_export.to_excel(writer, sheet_name='Attendance', index=False, header=True)
            
            # הוספת שורת סיכום
            workbook  = writer.book
            worksheet = writer.sheets['Attendance']
            
            # חישוב סיכומים
            total_hours_str = df['hours'].str.split(':').apply(lambda x: int(x[0])*60 + int(x[1])).sum()
            total_hours_formatted = f"{int(total_hours_str // 60):02d}:{int(total_hours_str % 60):02d}"
            total_km = df['km'].sum()

            # פורמט טקסט
            bold_format = workbook.add_format({'bold': True, 'align': 'right', 'right_to_left': True})
            
            # כתיבת הסיכום בשורה האחרונה
            last_row = len(df_export) + 1
            if 'שעות' in headers_heb:
                col_h = headers_heb.index('שעות')
                worksheet.write(last_row, col_h, f'סה״כ שעות: {total_hours_formatted}', bold_format)
            if 'ק״מ' in headers_heb:
                col_km = headers_heb.index('ק״מ')
                worksheet.write(last_row, col_km, f'סה״כ ק״מ: {total_km:.1f}', bold_format)

            writer.close()
            return output.getvalue()
        
        if 'last_rendered_df' in st.session_state and not st.session_state.last_rendered_df.empty:
            df_to_export = st.session_state.last_rendered_df
            excel_data = to_excel(df_to_export, {'include_id': include_id})
            
            st.download_button(
                label="ייצוא XLSX ($BINARY$)",
                data=excel_data,
                file_name=f"attendance_filtered_{datetime.now().strftime('%Y%m%d')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                key='export_filtered_xlsx'
            )
        else:
            st.info("אין נתונים מסוננים לייצוא.")

    # --- ייצוא חודשי ---
    with col_monthly:
        st.markdown('<h4 style="color:#00ff7f;">ייצוא חודשי ($MONTHLY\_REPORT$)</h4>', unsafe_allow_html=True)
        month_input = st.date_input("בחר חודש לייצוא", value=datetime.today(), format="MM/YYYY")

        if month_input:
            export_month = month_input.strftime('%Y-%m')
            
            # סינון רקורדים לחודש הנבחר ולמשתמש הנוכחי
            monthly_df = st.session_state.records_df[
                (st.session_state.records_df['date'].str.startswith(export_month))
            ].copy()
            
            # אם לא אדמין/מנהל, הצג רק רשומות של המשתמש
            if st.session_state.user_role == 'instructor':
                monthly_df = monthly_df[monthly_df['empNumber'] == st.session_state.emp_number]

            if not monthly_df.empty:
                excel_data_monthly = to_excel(monthly_df, {'include_id': include_id})
                
                emp_prefix = st.session_state.emp_number
                filename = f"תעשיידע_{emp_prefix}_{export_month}_נוכחות.xlsx"

                st.download_button(
                    label=f"ייצוא XLSX לחודש {export_month}",
                    data=excel_data_monthly,
                    file_name=filename,
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    key='export_monthly_xlsx'
                )
            else:
                st.info("לא נמצאו רשומות עבור חודש זה.")

def admin_users_tab():
    """טבלת ניהול משתמשים (Admin Only)."""
    st.subheader("ניהול משתמשים ($USER\_MATRIX$)")
    
    # הצגת טבלת המשתמשים
    users_display_df = st.session_state.users_df.copy()
    users_display_df['pin_masked'] = users_display_df['pin'].apply(lambda x: '•' * len(str(x)))
    users_display_df['role_heb'] = users_display_df['role'].map(ROLES)
    
    st.dataframe(users_display_df[['name', 'empNumber', 'role_heb', 'pin_masked']],
                 use_container_width=True, hide_index=True,
                 column_names={'name': 'שם', 'empNumber': 'מס׳ עובד', 'role_heb': 'תפקיד', 'pin_masked': 'PIN'})

    # פונקציית עדכון משתמשים פשוטה
    st.info("⚠️ בגרסה זו, ניהול המשתמשים הוא להצגה בלבד. יש לערוך את הקובץ users_data.xlsx ישירות להוספה/מחיקה.")

# ==================================================
# ==== [MAIN_EXECUTION] ====
# ==================================================

# אתחול נתונים ו-session state
init_data()

# הגדרת מצב כניסה ראשוני
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.emp_number = None

# ניתוב תצוגה
if st.session_state.logged_in:
    main_app_view()
else:
    login_view()