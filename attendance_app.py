import streamlit as st
import pandas as pd
import os
from datetime import datetime
from io import BytesIO

# ==================================================
# ==== [SYSTEM_CONFIG & CONSTANTS] ====
# ==================================================

USERS_FILE = "users_data.xlsx"
RECORDS_FILE = "records_data.xlsx"

ROLES = { 'admin': 'Admin', 'manager': 'מנהל', 'instructor': 'מדריך' }
PROGRAMS = ['ביומימיקרי','בינה מלאכותית','רוקחים עולם','טכנולוגיות החלל','יישומי AI','פורצות דרך','מנהיגות ירוקה','השמיים אינם הגבול','ביומימיקרי לחטיבות','טכנו-כיף','תמיר','חוצה ישראל','מקורות']
MUNICIPALITIES = ['אופקים','אשדוד','אשכול','אשקלון','באר יעקב','באר שבע','חדרה','חיפה','יבנה','לכיש','מ.א חוף אשקלון','מודיעין','מטה יהודה','מסעדה','נהריה','נתניה','עין אלאסד','עין קניא (רשות)','עכו','עמק הירדן','צפון + דרום','קריית גת','ראשון לציון','רחובות','רמלה','שדות דן','שדרות','שפיר','יד בנימין','הרצליה','קריית שמונה','בנימינה','נצרת','עפולה','בית שאן','ירוחם','אחר, לציין בהערות.']
ACTIVITY_TYPES = ['הכשרה','קורסים','סדנאות','סיורים','ביטול זמן']

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

# הזרקת CSS לעיצוב טכנולוגי קומפקטי (Neo-Grid/Cyberpunk)
st.markdown("""
<style>
/* צבעים גלובליים */
:root {
    --bg: #000000;
    --neo-cyan: #00ffff;
    --neo-green: #00ff7f;
}

/* רקע ופונט */
body {
    background: var(--bg);
    font-family: 'Consolas', 'Courier New', monospace;
    direction: rtl;
    color: var(--neo-green);
}

/* כותרות */
h1, h2, h3 {
    text-align: center;
    color: var(--neo-cyan);
    font-weight: bold;
    text-shadow: 0 0 10px rgba(0, 255, 255, 0.7);
}
.tab-content h3 { /* כותרות בתוך הטאבים */
    text-align: right;
    color: var(--neo-green);
    text-shadow: none;
    font-size: 1.25em;
    margin-bottom: 1rem;
    padding-bottom: 0.5rem;
    border-bottom: 1px dashed rgba(0, 255, 127, 0.3);
}

/* לוגין קארד */
.login-card {
    max-width: 450px;
    margin: 80px auto 40px;
    background: rgba(0, 0, 0, 0.7);
    padding: 2.5em;
    border-radius: 5px;
    box-shadow: 0 0 25px rgba(0, 255, 255, 0.6), 0 0 5px rgba(0, 255, 255, 0.4);
    text-align: center;
    border: 1px solid var(--neo-cyan);
}

/* טאב בר (כפתורי ניווט) */
.tab-bar {
    display: flex;
    gap: 8px;
    margin-bottom: 20px;
    flex-wrap: wrap;
}
.tab-button {
    padding: 8px 15px;
    border-radius: 5px;
    font-weight: bold;
    cursor: pointer;
    transition: 0.2s;
    border: 1px solid var(--neo-green);
    background: #1a1a1a;
    color: var(--neo-green);
    box-shadow: 0 0 5px rgba(0, 255, 127, 0.5);
}
.tab-button.active {
    background: var(--neo-cyan);
    color: #000000;
    border-color: var(--neo-cyan);
    box-shadow: 0 0 10px var(--neo-cyan);
}
.stButton button { /* איפוס כפתורי הטאבים כדי שלא ייראו כפתורים רגילים */
    padding: 0;
    background: none;
    border: none;
    box-shadow: none;
    color: inherit;
    font-size: 1em;
}

/* קומפקטיות של שדות קלט */
div[data-testid="stForm"] > div {
    padding: 0; /* מוריד ריפודים פנימיים בטופס */
}
div[data-testid="column"] {
    padding: 0 8px !important; /* ריווח קטן יותר בין עמודות */
}

/* שדות קלט */
div[data-testid="stTextInput"] input, 
div[data-testid="stDateInput"] input,
div[data-testid="stTimeInput"] input,
div[data-testid="stNumberInput"] input,
div[data-testid="stSelectbox"] div[role="combobox"] {
    font-size: 1.0em !important;
    border-radius: 0 !important;
    padding: 0.6em !important;
    background-color: #000000 !important;
    border: 1px solid var(--neo-green) !important;
    color: var(--neo-green) !important;
    box-shadow: 0 0 2px var(--neo-green) !important;
}

/* דאטה פריים */
.stDataFrame {
    direction: ltr !important;
    border: 1px solid var(--neo-cyan);
    box-shadow: 0 0 10px rgba(0, 255, 255, 0.3);
    margin-top: 15px;
}
</style>
""", unsafe_allow_html=True)


# ==================================================
# ==== [HELPER_FUNCTIONS] ====
# ==================================================

def calc_hours(start_time, end_time):
    """מחשב הפרש שעות בין שני אובייקטי datetime.time ומחזיר מחרוזת HH:MM."""
    if not start_time or not end_time: return ""
    try:
        start_dt = datetime.combine(datetime.min.date(), start_time)
        end_dt = datetime.combine(datetime.min.date(), end_time)
        if end_dt < start_dt: end_dt = end_dt.replace(day=end_dt.day + 1)
        
        diff = end_dt - start_dt
        total_minutes = int(diff.total_seconds() / 60)
        
        hours = total_minutes // 60
        minutes = total_minutes % 60
        return f"{hours:02d}:{minutes:02d}"
    except Exception:
        return ""

def init_data():
    """טוען או יוצר את קבצי הנתונים ומאתחל את מצב ה-session."""
    # משתמשי ברירת מחדל
    if not os.path.exists(USERS_FILE):
        pd.DataFrame(DEFAULT_USERS).to_excel(USERS_FILE, index=False)
    # נתוני נוכחות
    if not os.path.exists(RECORDS_FILE):
        pd.DataFrame(columns=['id', 'empNumber', 'empName', 'date', 'start', 'end', 'hours', 'type', 'municipality', 'location', 'program', 'meetingNumber', 'km', 'notes']).to_excel(RECORDS_FILE, index=False)

    # טעינת DataFrame-ים למצב session
    if 'users_df' not in st.session_state:
        st.session_state.users_df = pd.read_excel(USERS_FILE, dtype={'empNumber': str, 'pin': str})
    if 'records_df' not in st.session_state:
        st.session_state.records_df = pd.read_excel(RECORDS_FILE, dtype={'empNumber': str, 'meetingNumber': 'Int64'})
        
    # מצב כניסה וטאב נוכחי
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    if 'current_tab' not in st.session_state:
        st.session_state.current_tab = 'form'


def save_data(df, filename):
    """שומר DataFrame לקובץ Excel."""
    try:
        df.to_excel(filename, index=False)
    except Exception as e:
        st.error(f"שגיאה בשמירת קובץ הנתונים {filename}: {e}")

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
    
    # 4. סינון לפי סוג, רשות, תוכנית
    for key in ['type', 'municipality', 'program']:
        if filters.get(key) and filters[key] != 'הכל':
            filtered_df = filtered_df[filtered_df[key].fillna('') == filters[key]]

    filtered_df = filtered_df.sort_values(by=['date', 'start'], ascending=False)
    return filtered_df.reset_index(drop=True)

# ==================================================
# ==== [VIEWS] ====
# ==================================================

def login_view():
    """ממשק כניסה קומפקטי."""
    st.markdown('<div class="login-card">', unsafe_allow_html=True)
    st.markdown("<h2>כניסה למערכת: אימות ($ACCESS$)</h2>", unsafe_allow_html=True)

    with st.form("login_form"):
        col1, col2 = st.columns(2)
        with col1:
            emp_number = st.text_input("מס׳ עובד (4 ספרות)", max_chars=4, key='login_emp')
        with col2:
            pin = st.text_input("קוד PIN", type="password", max_chars=4, key='login_pin')
        
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
    """מנתק את המשתמש."""
    st.session_state.logged_in = False
    st.session_state.emp_number = None
    st.session_state.user_name = None
    st.session_state.user_role = None
    st.rerun()

def main_app_view():
    """ממשק האפליקציה הראשי עם Tab Bar מותאם."""
    
    # --- Header & User Info ---
    col_title, col_user, col_logout = st.columns([5, 2, 1])
    with col_title:
        st.markdown("<h1>📋 מערכת נוכחות תעשיידע</h1>", unsafe_allow_html=True)
    with col_user:
        role_label = ROLES.get(st.session_state.user_role, 'אורח')
        st.markdown(f"""
            <div style="text-align: left; margin-top: 15px;">
                <div style="color:var(--neo-cyan); font-weight:bold;">{st.session_state.user_name}</div>
                <div style="color:var(--neo-green); font-size:0.9em;">{role_label} • {st.session_state.emp_number}</div>
            </div>
            """, unsafe_allow_html=True)
    with col_logout:
        st.button("ניתוק ($LOGOUT$)", on_click=logout, key='logout_btn')

    st.markdown("---")

    # --- Tab Bar (Compact) ---
    tab_buttons = ['form', 'table', 'export']
    tab_labels = {'form': 'רישום נוכחות', 'table': 'דוחות וטבלה', 'export': 'ייצוא נתונים'}
    
    if st.session_state.user_role in ['admin', 'manager']:
        tab_buttons.append('users')
        tab_labels['users'] = 'ניהול משתמשים'

    cols = st.columns(len(tab_buttons) + 1)
    for i, tab_key in enumerate(tab_buttons):
        btn_class = "tab-button active" if st.session_state.current_tab == tab_key else "tab-button"
        if cols[i].button(tab_labels[tab_key], key=f'tab_{tab_key}'):
            st.session_state.current_tab = tab_key
            st.rerun()
        # הזרקת ה-CSS Class לכפתור
        cols[i].markdown(f'<style>div[data-testid="stButton"] button[data-testid="stFormSubmitButton-tab_{tab_key}"] {{ {btn_class} }}</style>', unsafe_allow_html=True)

    st.markdown('<div class="tab-content" style="padding-top: 20px;">', unsafe_allow_html=True)
    
    # --- Content Rendering ---
    if st.session_state.current_tab == 'form':
        attendance_form_tab()
    elif st.session_state.current_tab == 'table':
        data_grid_tab()
    elif st.session_state.current_tab == 'export':
        export_tab()
    elif st.session_state.current_tab == 'users':
        admin_users_tab()

    st.markdown('</div>', unsafe_allow_html=True)

# ==================================================
# ==== [TAB CONTENT: IMPLEMENTATIONS] ====
# ==================================================

def attendance_form_tab():
    """טופס רישום נוכחות (Create/Update)."""
    st.subheader("טופס רישום / עדכון פעילות ($DATA\_INPUT$)")
    
    # קריאה לפונקציית עדכון שעות אוטומטי
    def update_hours():
        start = st.session_state.start_time
        end = st.session_state.end_time
        st.session_state.hours_calculated = calc_hours(start, end)
    
    if 'hours_calculated' not in st.session_state:
        st.session_state.hours_calculated = calc_hours(datetime.now().time(), datetime.now().time())
    
    with st.form("attendance_form", clear_on_submit=True):
        st.markdown('<div style="color:#00ff7f; font-weight:bold;">זמן ומשך ($TIMESTAMP$)</div>', unsafe_allow_html=True)
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            date = st.date_input("תאריך", value=datetime.today(), key='date_input')
        with col2:
            start_time = st.time_input("שעת התחלה", value=datetime.now().time(), key='start_time', on_change=update_hours)
        with col3:
            end_time = st.time_input("שעת סיום", value=datetime.now().time(), key='end_time', on_change=update_hours)
        with col4:
            st.text_input("סה״כ שעות (מחושב)", value=st.session_state.hours_calculated, disabled=True)
        with col5:
            meeting_number = st.number_input("מס׳ מפגש", min_value=1, step=1, key='meetingNumber_input', format='%d')

        st.markdown("---")
        st.markdown('<div style="color:#00ff7f; font-weight:bold;">פרטי פעילות ($ACTIVITY\_PARAMS$)</div>', unsafe_allow_html=True)
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
                    'hours': st.session_state.hours_calculated,
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
                st.session_state.hours_calculated = calc_hours(datetime.now().time(), datetime.now().time()) # איפוס
                
def data_grid_tab():
    """דוחות וטבלת סינון (Read & Filter)."""
    st.subheader("דוח נוכחות: גריד נתונים ($DATA\_GRID$)")

    # --- סינון קומפקטי ---
    if 'filters' not in st.session_state:
        st.session_state.filters = {'from_date': None, 'to_date': None, 'type': 'הכל', 'municipality': 'הכל', 'program': 'הכל', 'emp': 'הכל'}

    col_filter1, col_filter2, col_filter3, col_filter4 = st.columns([1, 1, 1, 1])

    with col_filter1:
        st.date_input("מתאריך", value=st.session_state.filters['from_date'], key='from_date_filter', on_change=lambda: st.session_state.filters.update({'from_date': st.session_state.from_date_filter}))
        st.date_input("עד תאריך", value=st.session_state.filters['to_date'], key='to_date_filter', on_change=lambda: st.session_state.filters.update({'to_date': st.session_state.to_date_filter}))

    with col_filter2:
        st.selectbox("סוג פעילות", ['הכל'] + ACTIVITY_TYPES, index=(['הכל'] + ACTIVITY_TYPES).index(st.session_state.filters['type']), key='type_filter', on_change=lambda: st.session_state.filters.update({'type': st.session_state.type_filter}))
        st.selectbox("רשות", ['הכל'] + MUNICIPALITIES, index=(['הכל'] + MUNICIPALITIES).index(st.session_state.filters['municipality']), key='municipality_filter', on_change=lambda: st.session_state.filters.update({'municipality': st.session_state.municipality_filter}))

    with col_filter3:
        st.selectbox("תוכנית", ['הכל'] + PROGRAMS, index=(['הכל'] + PROGRAMS).index(st.session_state.filters['program']), key='program_filter', on_change=lambda: st.session_state.filters.update({'program': st.session_state.program_filter}))

        # סינון מדריך (רק למנהל/אדמין)
        if st.session_state.user_role in ['admin', 'manager']:
            emp_list = ['הכל'] + st.session_state.users_df['empNumber'].tolist()
            st.selectbox("מדריך", emp_list, index=emp_list.index(st.session_state.filters['emp']), key='emp_filter', on_change=lambda: st.session_state.filters.update({'emp': st.session_state.emp_filter}))
        else:
            st.session_state.filters.pop('emp', None)
    
    with col_filter4:
        st.markdown("<br>", unsafe_allow_html=True) # רווח עליון
        if st.button("נקה מסננים", key='clear_filters', type='secondary', use_container_width=True):
            st.session_state.filters = {'from_date': None, 'to_date': None, 'type': 'הכל', 'municipality': 'הכל', 'program': 'הכל', 'emp': 'הכל'}
            st.rerun()

    # החלת סינון וחישוב נתונים מסוננים
    filtered_df = get_filtered_records(st.session_state.records_df, st.session_state.filters)
    st.session_state.last_rendered_df = filtered_df
    
    if filtered_df.empty:
        st.info("⚡ [STANDBY MODE] לא נמצאו רשומות תואמות למסננים.")
    else:
        # --- סיכומים ---
        total_hours_str = filtered_df['hours'].str.split(':').apply(lambda x: int(x[0])*60 + int(x[1])).sum()
        total_hours_formatted = f"{int(total_hours_str // 60):02d}:{int(total_hours_str % 60):02d}"
        total_km = filtered_df['km'].sum()
        
        col_sum1, col_sum2, _ = st.columns([1, 1, 3])
        with col_sum1:
            st.markdown(f"**סה״כ שעות:** <span style='color:#00ffff; font-size:1.2em;'>{total_hours_formatted}</span>", unsafe_allow_html=True)
        with col_sum2:
            st.markdown(f"**סה״כ ק״מ:** <span style='color:#00ffff; font-size:1.2em;'>{total_km:.1f}</span>", unsafe_allow_html=True)

        # טבלת נתונים
        column_order = ['empName', 'empNumber', 'date', 'start', 'end', 'hours', 'type', 'municipality', 'location', 'program', 'meetingNumber', 'km', 'notes']
        
        st.dataframe(filtered_df[column_order], use_container_width=True, hide_index=True,
                     column_names={
                         'empName': 'שם עובד', 'empNumber': 'מס׳ עובד', 'date': 'תאריך', 'start': 'התחלה', 
                         'end': 'סיום', 'hours': 'שעות', 'type': 'סוג פעילות', 'municipality': 'רשות', 
                         'location': 'מיקום', 'program': 'תוכנית', 'meetingNumber': 'מס׳ מפגש', 'km': 'ק״מ', 
                         'notes': 'הערות'
                     })


def to_excel(df, opts):
    """המרת DataFrame ל-Bytes (Excel) כולל עמודות סיכום וכותרות."""
    output = BytesIO()
    writer = pd.ExcelWriter(output, engine='xlsxwriter')
    
    keys = ['empNumber', 'empName', 'date', 'start', 'end', 'hours', 'type', 'municipality', 'location', 'program', 'meetingNumber', 'km', 'notes']
    headers_heb = ['מס׳ עובד', 'שם עובד', 'תאריך', 'התחלה', 'סיום', 'שעות', 'סוג פעילות', 'רשות', 'מיקום', 'תוכנית', 'מס׳ מפגש', 'ק״מ', 'הערות']
    
    if opts.get('include_id'):
        keys.insert(0, 'id')
        headers_heb.insert(0, 'מזהה')

    df_export = df.copy()
    df_export = df_export[keys] # סידור עמודות לפי המפתחות
    if opts.get('heb_headers'):
        df_export.columns = headers_heb # שינוי כותרות
    
    df_export.to_excel(writer, sheet_name='Attendance', index=False, header=True)
    
    # הוספת שורת סיכום
    workbook  = writer.book
    worksheet = writer.sheets['Attendance']
    
    total_hours_str = df['hours'].str.split(':').apply(lambda x: int(x[0])*60 + int(x[1])).sum()
    total_hours_formatted = f"{int(total_hours_str // 60):02d}:{int(total_hours_str % 60):02d}"
    total_km = df['km'].sum()

    bold_format = workbook.add_format({'bold': True, 'align': 'right', 'right_to_left': True})
    
    last_row = len(df_export) + 1
    
    # כתיבת הסיכום בשורה האחרונה
    if 'שעות' in headers_heb:
        col_h = headers_heb.index('שעות')
        worksheet.write(last_row, col_h, f'סה״כ שעות: {total_hours_formatted}', bold_format)
    if 'ק״מ' in headers_heb:
        col_km = headers_heb.index('ק״מ')
        worksheet.write(last_row, col_km, f'סה״כ ק״מ: {total_km:.1f}', bold_format)

    writer.close()
    return output.getvalue()


def export_tab():
    """ממשק ייצוא נתונים (Export)."""
    st.subheader("ייצוא נתונים ($DATA\_EXFILTRATION$)")
    
    # --- הגדרות ---
    with st.container():
        st.markdown('<div style="color:#00ff7f; font-weight:bold;">העדפות ייצוא ($OPTIONS$)</div>', unsafe_allow_html=True)
        col_opt1, col_opt2 = st.columns(2)
        with col_opt1:
            heb_headers = st.checkbox("כותרות עמודות בעברית", value=True, key='opt_heb')
        with col_opt2:
            include_id = st.checkbox("כלול מזהה פנימי (id)", value=False, key='opt_id')

    st.markdown("---")

    col_filtered, col_monthly = st.columns(2)

    # --- ייצוא מסונן ---
    with col_filtered:
        st.markdown('<div style="color:#00ff7f; font-weight:bold;">ייצוא לפי המסננים הנוכחיים ($GRID\_VIEW$)</div>', unsafe_allow_html=True)
        
        if 'last_rendered_df' in st.session_state and not st.session_state.last_rendered_df.empty:
            df_to_export = st.session_state.last_rendered_df
            excel_data = to_excel(df_to_export, {'include_id': include_id, 'heb_headers': heb_headers})
            
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
        st.markdown('<div style="color:#00ff7f; font-weight:bold;">ייצוא חודשי ($MONTHLY\_REPORT$)</div>', unsafe_allow_html=True)
        month_input = st.date_input("בחר חודש לייצוא", value=datetime.today(), format="MM/YYYY", key='export_month_picker')

        if month_input:
            export_month = month_input.strftime('%Y-%m')
            
            # סינון רקורדים לחודש הנבחר
            monthly_df = st.session_state.records_df[
                (st.session_state.records_df['date'].str.startswith(export_month))
            ].copy()
            
            # אם לא אדמין/מנהל, הצג רק רשומות של המשתמש
            if st.session_state.user_role == 'instructor':
                monthly_df = monthly_df[monthly_df['empNumber'] == st.session_state.emp_number]

            if not monthly_df.empty:
                excel_data_monthly = to_excel(monthly_df, {'include_id': include_id, 'heb_headers': heb_headers})
                
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
    
    users_display_df = st.session_state.users_df.copy()
    users_display_df['pin_masked'] = users_display_df['pin'].apply(lambda x: '•' * len(str(x)))
    users_display_df['role_heb'] = users_display_df['role'].map(ROLES)
    
    st.dataframe(users_display_df[['name', 'empNumber', 'role_heb', 'pin_masked']],
                 use_container_width=True, hide_index=True,
                 column_names={'name': 'שם', 'empNumber': 'מס׳ עובד', 'role_heb': 'תפקיד', 'pin_masked': 'PIN'})

    st.info("⚠️ בגרסה זו, ניהול המשתמשים הוא להצגה בלבד. יש לערוך את הקובץ users_data.xlsx ישירות להוספה/מחיקה.")

# ==================================================
# ==== [MAIN_EXECUTION] ====
# ==================================================

# אתחול נתונים
init_data()

# ניתוב תצוגה
if st.session_state.logged_in:
    main_app_view()
else:
    login_view()
