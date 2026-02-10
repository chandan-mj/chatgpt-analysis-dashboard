"""
Streamlit Application: Analyzing the Role of ChatGPT in Enhancing Programming Skills
Academic Research Project - Production Ready
"""

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from io import StringIO
# import reff
from wordcloud import WordCloud
import warnings
warnings.filterwarnings('ignore')

# Page Configuration
st.set_page_config(
    page_title="ChatGPT Programming Skills Analysis",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for Professional Academic Theme
st.markdown("""
<style>
    /* Dark Blue Professional Theme */
    .main {
        background-color: #f5f7fa;
    }
    
    .stApp {
        background: linear-gradient(linear-gradient(135deg, #00ffff, #000000, #ffffff);
    }
            
   /* Login + dashboard content text */
    .login-container,
    .metric-card,
    .insight-box,
    .info-box,
    .dashboard-header,
    .dashboard-header *,
    .metric-card *,
    .insight-box *,
    .info-box * {
        color: #000000 ;
    }

    
    /* Login Container */
 
.login-title {
    color: #ffffff;
    font-size: 2.2rem;
    font-weight: 700;
    text-align: center;
    margin: 0 0 2rem 0;
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}



     .login-container {
         max-width: 700px;     /* controls form width */
         margin: 0 auto;       /* centers horizontally */
         text-align: center;   /* centers title & text */
       }



    /* Dashboard Headers */
    .dashboard-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 2rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        text-align: center;
    }
    
    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        margin-bottom: 1rem;
    }
    
    .insight-box {
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
        font-weight: 500;
    }
    
    .insight-improved {
        background-color: #d1fae5;
        border-left: 4px solid #10b981;
        color: #065f46;
    }
    
    .insight-neutral {
        background-color: #fef3c7;
        border-left: 4px solid #f59e0b;
        color: #92400e;
    }
    
    .insight-needs-improvement {
        background-color: #fee2e2;
        border-left: 4px solid #ef4444;
        color: #991b1b;
    }
    
    /* Buttons */
    .stButton>button {
        width: auto;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 0.75rem;
        border-radius: 8px;
        font-weight: 600;
        font-size: 1rem;
        transition: transform 0.2s;
    }
  

    
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
    }
    
    /* Info boxes */
    .info-box {
        background: #eff6ff;
        border-left: 4px solid #3b82f6;
        padding: 1rem;
        border-radius: 5px;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# ==================== AUTHENTICATION CREDENTIALS ====================
CREDENTIALS = {
    'admin': {
        'email': 'admin@college.edu',
        'password': 'admin123',
        'role': 'Admin'
    },
    'teacher': {
        'email': 'teacher@college.edu',
        'password': 'teacher123',
        'role': 'Teacher'
    }
}

# ==================== HELPER FUNCTIONS ====================

def clean_column_names(df):
    """Clean and standardize column names"""
    df.columns = df.columns.str.strip().str.replace(r'\s+', '', regex=True)
    return df

def detect_email_column(df):
    """Dynamically detect email column"""
    for col in df.columns:
        if 'email' in col.lower():
            return col
    return None

def detect_name_column(df):
    """Dynamically detect name column"""
    for col in df.columns:
        if 'name' in col.lower() and 'user' not in col.lower():
            return col
    return None

def extract_email_prefix(email):
    """Extract prefix from email (before @)"""
    if pd.isna(email) or not isinstance(email, str):
        return None
    return email.split('@')[0].lower()

def safe_numeric_conversion(series):
    """Safely convert series to numeric"""
    return pd.to_numeric(series, errors='coerce')

def categorize_improvement(pre_score, post_score):
    """Categorize improvement level"""
    if pd.isna(pre_score) or pd.isna(post_score):
        return "Insufficient Data"
    
    improvement = post_score - pre_score
    
    if improvement >= 50:
        return "✅ Excellent Improvement"
    elif improvement >= 20:
        return "✅ Strong Improvement"
    elif improvement >= 5:
        return "⚠️ Moderate Improvement"
    elif improvement >= -5:
        return "⚠️ Neutral"
    else:
        return "❌ Needs Improvement"

def get_insight_class(category):
    """Get CSS class for insight box"""
    if "Excellent" in category or "Strong" in category:
        return "insight-improved"
    elif "Moderate" in category or "Neutral" in category:
        return "insight-neutral"
    else:
        return "insight-needs-improvement"

# ==================== AUTHENTICATION FUNCTIONS ====================

def initialize_session():
    """Initialize session state variables"""
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    if 'user_email' not in st.session_state:
        st.session_state.user_email = None
    if 'user_role' not in st.session_state:
        st.session_state.user_role = None
    if 'user_name' not in st.session_state:
        st.session_state.user_name = None
    if 'uploaded_data' not in st.session_state:
        st.session_state.uploaded_data = None

def authenticate_user(email, password):
    """Authenticate user based on role"""
    email = email.lower().strip()
    password = password.strip()
    
    # Check Admin
    if email == CREDENTIALS['admin']['email'] and password == CREDENTIALS['admin']['password']:
        return True, 'Admin', 'Admin User'
    
    # Check Teacher
    if email == CREDENTIALS['teacher']['email'] and password == CREDENTIALS['teacher']['password']:
        return True, 'Teacher', 'Teacher User'
    
    # Check Student
    if st.session_state.uploaded_data is not None:
        df = st.session_state.uploaded_data
        email_col = detect_email_column(df)
        
        if email_col:
            student_row = df[df[email_col].str.lower().str.strip() == email]
            
            if not student_row.empty:
                expected_password = extract_email_prefix(email)
                if password.lower() == expected_password:
                    name_col = detect_name_column(df)
                    student_name = student_row.iloc[0][name_col] if name_col else "Student"
                    return True, 'Student', student_name
    
    return False, None, None

def logout():
    """Logout user and clear session"""
    st.session_state.authenticated = False
    st.session_state.user_email = None
    st.session_state.user_role = None
    st.session_state.user_name = None
    st.rerun()

# ==================== LOGIN PAGE ====================

def show_login_page():
    """Display login interface"""

    # OPEN white box
    st.markdown('<div class="login-container">', unsafe_allow_html=True)

    st.markdown(    '''
       <div style="max-width:700px; margin:0 auto; text-align:center;">
           <h1 class="login-title">🎓 Student, Teacher & Admin Login Portal</h1>
        </div>
        ''',
         unsafe_allow_html=True
)


    # ✅ FIXED typo + stays inside box
    st.markdown(
'<p style="color:#e38e0e; margin-bottom:2rem; text-align:center; max-width:700px; margin-left:auto; margin-right:auto;">'

        'ChatGPT Programming Skills Analysis System</p>',
        unsafe_allow_html=True
    )

    with st.form("login_form"):
        c1, c2, c3 = st.columns([1, 2, 1])
        with c2:
            email = st.text_input("📧 Email Address", placeholder="Enter your email")
            password = st.text_input("🔒 Password", type="password", placeholder="Enter your password")
            submit = st.form_submit_button("Login", use_container_width=True)

        if submit:
            if not email or not password:
                st.error("❌ Please enter both email and password")
            else:
                success, role, name = authenticate_user(email, password)
                if success:
                    st.session_state.authenticated = True
                    st.session_state.user_email = email
                    st.session_state.user_role = role
                    st.session_state.user_name = name
                    st.rerun()
                else:
                    st.error("❌ Invalid credentials.")
                    if st.session_state.uploaded_data is not None:
                        st.info("💡 For Students: Password is your email prefix (before @)")

    # CLOSE white box
    st.markdown('</div>', unsafe_allow_html=True)

    # About section (outside)
    st.markdown("---")
    st.markdown("""
    <div style="max-width: 800px; margin: 2rem auto; color: white; text-align: center;">
        <h3>📚 About This System</h3>
        <p>
            This platform analyzes the impact of ChatGPT on undergraduate programming skills
            through Pre-Test and Post-Test comparisons.
        </p>
    </div>
    """, unsafe_allow_html=True)
# ==================== ADMIN DASHBOARD ====================

def show_admin_dashboard():
    """Admin dashboard with data upload functionality"""
    st.markdown("""
    <div class="dashboard-header">
        <h1>👨‍💼 Admin Dashboard</h1>
        <p>Upload and manage research data</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns([3, 1])
    with col2:
        if st.button("🚪 Logout"):
            logout()
    
    st.markdown("### 📤 Upload Dataset")
    st.markdown('<div class="info-box">Upload CSV file exported from Google Forms. The system will automatically detect columns.</div>', unsafe_allow_html=True)
    
    uploaded_file = st.file_uploader("Choose CSV file", type=['csv'], key="admin_upload")
    
    if uploaded_file is not None:
        try:
            df = pd.read_csv(uploaded_file)
            df = clean_column_names(df)
            
            st.success(f"✅ File uploaded successfully! {len(df)} records found.")
            
            st.session_state.uploaded_data = df
            
            st.markdown("### 📊 Dataset Preview")
            st.dataframe(df.head(10), use_container_width=True)
            
            st.markdown("### 📈 Dataset Statistics")
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Total Records", len(df))
            with col2:
                st.metric("Total Columns", len(df.columns))
            with col3:
                email_col = detect_email_column(df)
                unique_students = df[email_col].nunique() if email_col else "N/A"
                st.metric("Unique Students", unique_students)
            with col4:
                missing_pct = (df.isnull().sum().sum() / (len(df) * len(df.columns)) * 100)
                st.metric("Missing Data %", f"{missing_pct:.1f}%")
            
            st.markdown("### 🔍 Detected Columns")
            cols_info = []
            for col in df.columns:
                dtype = str(df[col].dtype)
                null_count = df[col].isnull().sum()
                cols_info.append({
                    'Column': col,
                    'Type': dtype,
                    'Missing': null_count,
                    'Unique': df[col].nunique()
                })
            
            st.dataframe(pd.DataFrame(cols_info), use_container_width=True)
            
            # Download processed data
            csv = df.to_csv(index=False)
            st.download_button(
                label="📥 Download Processed Data",
                data=csv,
                file_name="processed_data.csv",
                mime="text/csv"
            )
            
        except Exception as e:
            st.error(f"❌ Error processing file: {str(e)}")
    
    # Show current dataset status
    if st.session_state.uploaded_data is not None:
        st.markdown("---")
        st.markdown("### ✅ Current Active Dataset")
        df = st.session_state.uploaded_data
        st.info(f"📊 {len(df)} records available for Teacher and Student access")
    else:
        st.warning("⚠️ No dataset uploaded yet. Please upload a CSV file to enable system access.")

# ==================== TEACHER DASHBOARD ====================

def show_teacher_dashboard():
    """Teacher dashboard with comprehensive analytics"""
    st.markdown("""
    <div class="dashboard-header">
        <h1>👨‍🏫 Teacher Dashboard</h1>
        <p>Comprehensive Analytics & Insights</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns([3, 1])
    with col2:
        if st.button("🚪 Logout"):
            logout()
    
    if st.session_state.uploaded_data is None:
        st.warning("⚠️ No data available. Please contact admin to upload dataset.")
        return
    
    df = st.session_state.uploaded_data.copy()
    
    # Detect key columns
    email_col = detect_email_column(df)
    name_col = detect_name_column(df)
    
    # Try to find Pre-Test and Post-Test columns
    pre_test_cols = [col for col in df.columns if 'pre' in col.lower() and 'score' in col.lower()]
    post_test_cols = [col for col in df.columns if 'post' in col.lower() and 'score' in col.lower()]
    
    # ==================== OVERVIEW METRICS ====================
    st.markdown("## 📊 Overview Metrics")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
            <div class="metric-card">
                <h3>Total Students</h3>
                <h1>123</h1>
            </div>
            """, unsafe_allow_html=True)

    
    with col2:
     if pre_test_cols:
        avg_pre = df[pre_test_cols[0]].mean()
        st.markdown(f"""
            <div class="metric-card">
                <h4>📝 Avg Pre-Test</h4>
                <h1>{avg_pre:.1f}%</h1>
            </div>
        """, unsafe_allow_html=True)

    
    with col3:
     if post_test_cols:
        avg_post = df[post_test_cols[0]].mean()
        st.markdown(f"""
            <div class="metric-card">
                <h4>✅ Avg Post-Test</h4>
                <h1>{avg_post:.1f}%</h1>
            </div>
        """, unsafe_allow_html=True)

    
    with col4:
     if pre_test_cols and post_test_cols:
        avg_improvement = df[post_test_cols[0]].mean() - df[pre_test_cols[0]].mean()
        st.markdown(f"""
            <div class="metric-card">
                <h4>📈 Avg Improvement</h4>
                <h1>{avg_improvement:+.1f}%</h1>
            </div>
        """, unsafe_allow_html=True)

    
    # ==================== VISUALIZATIONS ====================
    
    if pre_test_cols and post_test_cols:
        st.markdown("---")
        st.markdown("## 📈 Pre-Test vs Post-Test Analysis")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 📊 Score Distribution Comparison")
            fig, ax = plt.subplots(figsize=(10, 6))
            
            x = np.arange(len(df))
            width = 0.35
            
            pre_scores = df[pre_test_cols[0]].fillna(0)
            post_scores = df[post_test_cols[0]].fillna(0)
            
            ax.bar(x - width/2, pre_scores, width, label='Pre-Test', color='#ef4444', alpha=0.8)
            ax.bar(x + width/2, post_scores, width, label='Post-Test', color='#10b981', alpha=0.8)
            
            ax.set_xlabel('Student Index', fontsize=12, fontweight='bold')
            ax.set_ylabel('Score (%)', fontsize=12, fontweight='bold')
            ax.set_title('Pre-Test vs Post-Test Scores', fontsize=14, fontweight='bold', pad=20)
            ax.legend()
            ax.grid(axis='y', alpha=0.3)
            
            st.pyplot(fig)
            plt.close()
            
            st.markdown("""
            <div class="info-box">
            <strong>📌 Interpretation:</strong> This chart compares individual student scores before and after using ChatGPT.
            Green bars higher than red bars indicate improvement.
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("### 📊 Average Score Comparison")
            fig, ax = plt.subplots(figsize=(10, 6))
            
            categories = ['Pre-Test', 'Post-Test']
            scores = [df[pre_test_cols[0]].mean(), df[post_test_cols[0]].mean()]
            colors = ['#ef4444', '#10b981']
            
            bars = ax.bar(categories, scores, color=colors, alpha=0.8, edgecolor='black', linewidth=2)
            
            # Add value labels on bars
            for bar in bars:
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height,
                       f'{height:.1f}%',
                       ha='center', va='bottom', fontsize=14, fontweight='bold')
            
            ax.set_ylabel('Average Score (%)', fontsize=12, fontweight='bold')
            ax.set_title('Class Average Performance', fontsize=14, fontweight='bold', pad=20)
            ax.set_ylim(0, 110)
            ax.grid(axis='y', alpha=0.3)
            
            st.pyplot(fig)
            plt.close()
            
            improvement_pct = ((scores[1] - scores[0]) / scores[0] * 100) if scores[0] > 0 else 0
            st.markdown(f"""
            <div class="info-box">
            <strong>📌 Key Finding:</strong> Class average improved by {improvement_pct:.1f}% after using ChatGPT.
            </div>
            """, unsafe_allow_html=True)
        
        # Improvement Distribution
        st.markdown("---")
        st.markdown("### 📊 Improvement Distribution")
        
        df['Improvement'] = df[post_test_cols[0]] - df[pre_test_cols[0]]
        
        col1, col2 = st.columns(2)
        
        with col1:
            fig, ax = plt.subplots(figsize=(10, 6))
            
            colors_improvement = ['#10b981' if x >= 0 else '#ef4444' for x in df['Improvement']]
            ax.barh(range(len(df)), df['Improvement'], color=colors_improvement, alpha=0.8)
            
            ax.set_xlabel('Improvement (Post - Pre) %', fontsize=12, fontweight='bold')
            ax.set_ylabel('Student Index', fontsize=12, fontweight='bold')
            ax.set_title('Individual Student Improvement', fontsize=14, fontweight='bold', pad=20)
            ax.axvline(x=0, color='black', linestyle='--', linewidth=1)
            ax.grid(axis='x', alpha=0.3)
            
            st.pyplot(fig)
            plt.close()
        
        with col2:
            fig, ax = plt.subplots(figsize=(10, 6))
            
            improvement_categories = []
            for imp in df['Improvement']:
                if imp >= 50:
                    improvement_categories.append('Excellent (≥50%)')
                elif imp >= 20:
                    improvement_categories.append('Strong (20-49%)')
                elif imp >= 0:
                    improvement_categories.append('Moderate (0-19%)')
                else:
                    improvement_categories.append('Negative (<0%)')
            
            category_counts = pd.Series(improvement_categories).value_counts()
            
            colors_pie = ['#10b981', '#3b82f6', '#f59e0b', '#ef4444']
            ax.pie(category_counts.values, labels=category_counts.index, autopct='%1.1f%%',
                   colors=colors_pie, startangle=90)
            ax.set_title('Improvement Categories', fontsize=14, fontweight='bold', pad=20)
            
            st.pyplot(fig)
            plt.close()
        
        # Statistical Analysis
        st.markdown("---")
        st.markdown("### 📊 Statistical Analysis")
        
        col1, col2, col3 = st.columns(3)
        
    with col1:
        improved = (df['Improvement'] > 0).sum()
        st.markdown(f"""
            <div class="metric-card">
                <h4>✅ Students Improved</h4>
                <h1>{improved}</h1>
            </div>
    """, unsafe_allow_html=True)

        
        with col2:
            neutral = (df['Improvement'] == 0).sum()
            st.markdown(f"""
                <div class="metric-card">
                  <h4>➖ No Change</h4>
                  <h1>{neutral}</h1>
        </div>
    """, unsafe_allow_html=True)

        
        with col3:
            declined = (df['Improvement'] < 0).sum()
            st.markdown(f"""
               <div class="metric-card">
                    <h4>⚠️ Declined</h4>
                    <h1>{declined}</h1>
        </div>
    """, unsafe_allow_html=True)

    # ==================== ADDITIONAL ANALYSIS ====================
    
    # Check for additional columns
    other_numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    
    if len(other_numeric_cols) > 2:
        st.markdown("---")
        st.markdown("## 🔍 Additional Metrics Analysis")
        
        # Correlation Heatmap
        st.markdown("### 🔥 Correlation Heatmap")
        numeric_df = df[other_numeric_cols].dropna()
        
        if not numeric_df.empty:
            fig, ax = plt.subplots(figsize=(12, 8))
            correlation = numeric_df.corr()
            sns.heatmap(correlation, annot=True, fmt='.2f', cmap='coolwarm', 
                       center=0, square=True, ax=ax, cbar_kws={'label': 'Correlation'})
            ax.set_title('Correlation Between Metrics', fontsize=14, fontweight='bold', pad=20)
            st.pyplot(fig)
            plt.close()
            
            st.markdown("""
            <div class="info-box">
            <strong>📌 About Correlation:</strong> Values close to +1 indicate strong positive relationship,
            values close to -1 indicate strong negative relationship, and values near 0 indicate weak relationship.
            </div>
            """, unsafe_allow_html=True)
    
    # ==================== DATA EXPORT ====================
    st.markdown("---")
    st.markdown("## 📥 Export Data")
    
    col1, col2 = st.columns(2)
    
    with col1:
        csv = df.to_csv(index=False)
        st.download_button(
            label="📊 Download Full Dataset",
            data=csv,
            file_name="complete_analysis.csv",
            mime="text/csv",
            use_container_width=True
        )
    
    with col2:
        if 'Improvement' in df.columns:
            summary_df = df[[name_col, email_col, pre_test_cols[0], post_test_cols[0], 'Improvement']].copy()
            csv_summary = summary_df.to_csv(index=False)
            st.download_button(
                label="📈 Download Summary Report",
                data=csv_summary,
                file_name="improvement_summary.csv",
                mime="text/csv",
                use_container_width=True
            )

# ==================== STUDENT DASHBOARD ====================

def show_student_dashboard():
    """Student dashboard with personal analytics"""
    st.markdown(f"""
    <div class="dashboard-header">
        <h1>🎓 Student Dashboard</h1>
        <p>Welcome, {st.session_state.user_name}!</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns([3, 1])
    with col2:
        if st.button("🚪 Logout"):
            logout()
    
    if st.session_state.uploaded_data is None:
        st.warning("⚠️ No data available. Please contact admin.")
        return
    
    df = st.session_state.uploaded_data.copy()
    
    # Get student's data
    email_col = detect_email_column(df)
    student_data = df[df[email_col].str.lower().str.strip() == st.session_state.user_email.lower()]
    
    if student_data.empty:
        st.error("❌ Your data not found in the system.")
        return
    
    student_row = student_data.iloc[0]
    
    # Detect columns
    name_col = detect_name_column(df)
    pre_test_cols = [col for col in df.columns if 'pre' in col.lower() and 'score' in col.lower()]
    post_test_cols = [col for col in df.columns if 'post' in col.lower() and 'score' in col.lower()]
    
    # ==================== PROFILE SECTION ====================
    st.markdown("## 👤 Your Profile")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown("**📧 Email**")
        st.write(student_row[email_col] if email_col else "N/A")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown("**👤 Name**")
        st.write(student_row[name_col] if name_col else "N/A")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col3:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        # Check for course/semester columns
        course_cols = [col for col in df.columns if 'course' in col.lower() or 'program' in col.lower()]
        if course_cols:
            st.markdown("**📚 Course**")
            st.write(student_row[course_cols[0]])
        else:
            st.markdown("**📚 Course**")
            st.write("N/A")
        st.markdown('</div>', unsafe_allow_html=True)
    
    # ==================== PERFORMANCE METRICS ====================
    st.markdown("---")
    st.markdown("## 📊 Your Performance")
    
    if pre_test_cols and post_test_cols:
        pre_score = student_row[pre_test_cols[0]]
        post_score = student_row[post_test_cols[0]]
        improvement = post_score - pre_score
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown(f"""
                 <div class="metric-card">
                      <h4>📝 Pre-Test Score</h4>
                      <h1>{pre_score:.1f}%</h1>
                 </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
                <div class="metric-card">
                  <h4>✅ Post-Test Score</h4>
                  <h1>{post_score:.1f}%</h1>
                </div>
            """, unsafe_allow_html=True)

        
        with col3:
            st.markdown(f"""
                <div class="metric-card">
                    <h4>📈 Improvement</h4>
                    <h1>{improvement:+.1f}%</h1>
                </div>
            """, unsafe_allow_html=True)
 
        
        # ==================== VISUALIZATION ====================
        st.markdown("---")
        st.markdown("### 📈 Your Progress Visualization")
        
        col1, col2 = st.columns(2)
        
        with col1:
            fig, ax = plt.subplots(figsize=(10, 6))
            
            categories = ['Pre-Test', 'Post-Test']
            scores = [pre_score, post_score]
            colors = ['#ef4444', '#10b981']
            
            bars = ax.bar(categories, scores, color=colors, alpha=0.8, edgecolor='black', linewidth=2)
            
            for bar in bars:
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height,
                       f'{height:.1f}%',
                       ha='center', va='bottom', fontsize=14, fontweight='bold')
            
            ax.set_ylabel('Score (%)', fontsize=12, fontweight='bold')
            ax.set_title('Your Score Comparison', fontsize=14, fontweight='bold', pad=20)
            ax.set_ylim(0, 110)
            ax.grid(axis='y', alpha=0.3)
            
            st.pyplot(fig)
            plt.close()
        
        with col2:
            # Comparison with class average
            fig, ax = plt.subplots(figsize=(10, 6))
            
            class_pre_avg = df[pre_test_cols[0]].mean()
            class_post_avg = df[post_test_cols[0]].mean()
            
            x = np.arange(2)
            width = 0.35
            
            bars1 = ax.bar(x - width/2, [pre_score, post_score], width, 
                          label='Your Scores', color='#667eea', alpha=0.8)
            bars2 = ax.bar(x + width/2, [class_pre_avg, class_post_avg], width,
                          label='Class Average', color='#f59e0b', alpha=0.8)
            
            ax.set_ylabel('Score (%)', fontsize=12, fontweight='bold')
            ax.set_title('You vs Class Average', fontsize=14, fontweight='bold', pad=20)
            ax.set_xticks(x)
            ax.set_xticklabels(['Pre-Test', 'Post-Test'])
            ax.legend()
            ax.grid(axis='y', alpha=0.3)
            
            st.pyplot(fig)
            plt.close()
        
        # ==================== INSIGHTS ====================
        st.markdown("---")
        st.markdown("## 💡 Personalized Insights")
        
        category = categorize_improvement(pre_score, post_score)
        css_class = get_insight_class(category)
        
        st.markdown(f'<div class="insight-box {css_class}">', unsafe_allow_html=True)
        st.markdown(f"### {category}")
        
        if "Excellent" in category:
            st.markdown("""
            🎉 **Outstanding Performance!** Your improvement demonstrates excellent utilization of ChatGPT 
            as a learning tool. You've shown significant growth in programming skills.
            
            **Key Achievements:**
            - Strong understanding of programming concepts
            - Effective use of AI assistance
            - Significant skill enhancement
            
            **Next Steps:** Continue leveraging ChatGPT for complex problems while maintaining your analytical skills.
            """)
        elif "Strong" in category:
            st.markdown("""
            ✅ **Great Progress!** You've made strong improvements in your programming skills with ChatGPT's assistance.
            
            **Key Achievements:**
            - Notable improvement in problem-solving
            - Good integration of AI tools
            
            **Next Steps:** Focus on challenging yourself with more complex problems to reach excellent level.
            """)
        elif "Moderate" in category or "Neutral" in category:
            st.markdown("""
            ⚠️ **Room for Growth** You've shown some improvement, but there's potential for better ChatGPT utilization.
            
            **Recommendations:**
            - Ask more detailed questions to ChatGPT
            - Verify and understand all suggested solutions
            - Practice implementing solutions independently
            
            **Next Steps:** Increase engagement with AI tools while focusing on fundamental understanding.
            """)
        else:
            st.markdown("""
            ⚠️ **Needs Attention** Your scores suggest difficulty in leveraging ChatGPT effectively.
            
            **Action Required:**
            - Review fundamental programming concepts
            - Learn how to ask better questions to AI
            - Seek additional support from teachers
            - Practice with simpler problems first
            
            **Next Steps:** Consider additional tutoring and structured practice sessions.
            """)
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Class ranking (percentile)
        st.markdown("---")
        st.markdown("## 📊 Your Class Standing")
        
        df_with_improvement = df.copy()
        df_with_improvement['Improvement'] = df[post_test_cols[0]] - df[pre_test_cols[0]]
        
        percentile = (df_with_improvement['Improvement'] < improvement).sum() / len(df_with_improvement) * 100
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown(f"""
               <div class="metric-card">
                    <h4>🎯 Your Percentile</h4>
                    <h1>{percentile:.0f}th</h1>
               </div>
            """, unsafe_allow_html=True)

        
        with col2:
            rank = len(df_with_improvement) - (df_with_improvement['Improvement'] < improvement).sum()
            st.markdown(f"""
               <div class="metric-card">
                    <h4>🏆 Class Rank</h4>
                    <h1>{rank}/{len(df_with_improvement)}</h1>
               </div>
            """, unsafe_allow_html=True)

        
        with col3:
            st.markdown(f"""
              <div class="metric-card">
                   <h4>📈 Class Avg Improvement</h4>
                   <h1>{df_with_improvement['Improvement'].mean():.1f}%</h1>
              </div>
        """, unsafe_allow_html=True)

    
    # Display all available data for the student
    st.markdown("---")
    st.markdown("## 📋 Your Complete Data")
    
    student_display = student_data.T
    student_display.columns = ['Value']
    st.dataframe(student_display, use_container_width=True)

# ==================== MAIN APPLICATION ====================

def main():
    """Main application logic"""
    initialize_session()
    
    if not st.session_state.authenticated:
        show_login_page()
    else:
        # Role-based routing
        if st.session_state.user_role == 'Admin':
            show_admin_dashboard()
        elif st.session_state.user_role == 'Teacher':
            show_teacher_dashboard()
        elif st.session_state.user_role == 'Student':
            show_student_dashboard()

if __name__ == "__main__":
    main()