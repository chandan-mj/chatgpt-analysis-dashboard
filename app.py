"""
Streamlit Dashboard: Analyzing the Role of ChatGPT in Enhancing Programming Skills
Among Undergraduate Students

This application provides role-based authentication for teachers and students
to view survey analytics on ChatGPT usage in programming education.

Authentication Logic:
- Teachers: Hardcoded credentials (teacher@gmail.com / teacher123)
- Students: Email must exist in CSV + common password (student123)

Role-Based Access:
- Teachers: Full dashboard with all student data and analytics
- Students: Only their own survey responses and comparison with class average
"""

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
try:
    from wordcloud import WordCloud
except ImportError:
    WordCloud = None
import numpy as np
from io import BytesIO
import os

# ==========================================
# CONFIGURATION & CONSTANTS
# ==========================================

# Teacher credentials (hardcoded as per requirements)
TEACHER_EMAIL = "teacher@gmail.com"
TEACHER_PASSWORD = "teacher123"

# Common student password (all students use this)
STUDENT_PASSWORD = "student123"

# CSV file path
CSV_FILE_PATH = "chatgpt_student_feedback.csv"

# Page configuration
st.set_page_config(
    page_title="ChatGPT Research Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==========================================
# CUSTOM CSS STYLING (Professional Academic Theme - Blue/Gray)
# ==========================================

def apply_custom_styles():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Source+Sans+Pro:wght@300;400;600;700&display=swap');
    
    /* Main app styling */
    .stApp {
        font-family: 'Source Sans Pro', sans-serif;
    }
    
    /* Header styling */
    .main-header {
        background: linear-gradient(135deg, #1e3a5f 0%, #2c5282 100%);
        padding: 2rem;
        border-radius: 12px;
        margin-bottom: 2rem;
        text-align: center;
        box-shadow: 0 4px 15px rgba(30, 58, 95, 0.3);
    }
    
    .main-header h1 {
        color: #ffffff;
        font-size: 2rem;
        font-weight: 700;
        margin: 0;
    }
    
    .main-header p {
        color: #e2e8f0;
        font-size: 1rem;
        margin-top: 0.5rem;
    }
    
    /* Login card styling */
    .login-card {
        background: #ffffff;
        padding: 2.5rem;
        border-radius: 16px;
        box-shadow: 0 10px 40px rgba(0, 0, 0, 0.12);
        max-width: 420px;
        margin: 2rem auto;
        border: 1px solid #e2e8f0;
    }
    
    .login-card h2 {
        color: #1e3a5f;
        text-align: center;
        font-size: 1.5rem;
        margin-bottom: 1.5rem;
        font-weight: 600;
    }
    
    /* Metric cards */
    .metric-card {
        background: #ffffff;
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 2px 10px rgba(0, 0, 0, 0.08);
        border-left: 4px solid #2c5282;
        margin-bottom: 1rem;
    }
    
    .metric-card h3 {
        color: #4a5568;
        font-size: 0.875rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin: 0;
    }
    
    .metric-card .value {
        color: #1e3a5f;
        font-size: 2rem;
        font-weight: 700;
        margin-top: 0.5rem;
    }
    
    /* Section headers */
    .section-header {
        color: #1e3a5f;
        font-size: 1.25rem;
        font-weight: 600;
        padding-bottom: 0.75rem;
        border-bottom: 2px solid #e2e8f0;
        margin-bottom: 1.5rem;
    }
    
    /* Sidebar styling */
    .css-1d391kg, [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1e3a5f 0%, #2c5282 100%);
    }
    
    [data-testid="stSidebar"] .stMarkdown {
        color: #ffffff;
    }
    
    /* Button styling */
    .stButton > button {
        background: linear-gradient(135deg, #2c5282 0%, #1e3a5f 100%);
        color: white;
        border: none;
        padding: 0.75rem 2rem;
        border-radius: 8px;
        font-weight: 600;
        transition: all 0.3s ease;
        width: 100%;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(44, 82, 130, 0.4);
    }
    
    /* DataFrames */
    .dataframe {
        font-size: 0.875rem;
    }
    
    /* Alert boxes */
    .stAlert {
        border-radius: 8px;
    }
    
    /* Success message */
    .success-msg {
        background: #c6f6d5;
        color: #22543d;
        padding: 1rem;
        border-radius: 8px;
        text-align: center;
        margin: 1rem 0;
    }
    
    /* Error message */
    .error-msg {
        background: #fed7d7;
        color: #c53030;
        padding: 1rem;
        border-radius: 8px;
        text-align: center;
        margin: 1rem 0;
    }
    
    /* Info box */
    .info-box {
        background: #ebf8ff;
        border-left: 4px solid #2c5282;
        padding: 1rem;
        border-radius: 0 8px 8px 0;
        margin: 1rem 0;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: #f7fafc;
        border-radius: 8px 8px 0 0;
        padding: 0.75rem 1.5rem;
        color: #4a5568;
    }
    
    .stTabs [aria-selected="true"] {
        background: #2c5282;
        color: white;
    }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# DATA LOADING & PROCESSING
# ==========================================

@st.cache_data
def load_data():
    """Load and preprocess the survey data from CSV."""
    try:
        df = pd.read_csv(CSV_FILE_PATH)
        
        # Clean column names - remove leading/trailing whitespace and newlines
        df.columns = df.columns.str.strip().str.replace('\n', ' ').str.replace('  ', ' ')
        
        # Standardize the consent column name
        consent_cols = [col for col in df.columns if 'I have read and agree' in col]
        if consent_cols:
            df = df.rename(columns={consent_cols[0]: 'Consent'})
        
        # Identify Likert scale columns (questions with numeric responses 1-5)
        likert_cols = []
        for col in df.columns:
            if col not in ['Timestamp', 'Email Address', 'Consent', 'Name', 'Course', 'Sem']:
                # Check if column contains numeric values
                if df[col].dtype in ['int64', 'float64'] or df[col].apply(lambda x: str(x).isdigit() if pd.notna(x) else True).all():
                    likert_cols.append(col)
        
        # Convert Likert columns to numeric
        for col in likert_cols:
            df[col] = pd.to_numeric(df[col], errors='coerce')
        
        # Standardize semester names to Roman numerals
        semester_map = {
            '1': 'I', '2': 'II', '3': 'III', '4': 'IV',
            '5': 'V', '6': 'VI', '7': 'VII', '8': 'VIII', '9': 'IX', '10': 'X'
        }
        if 'Sem' in df.columns:
            df['Sem'] = df['Sem'].astype(str).str.strip()
            df['Sem'] = df['Sem'].replace(semester_map)
        
        # Clean course names for better grouping
        if 'Course' in df.columns:
            df['Course'] = df['Course'].str.strip()
        
        return df, likert_cols
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        return None, []

def get_student_emails(df):
    """Extract all student emails from the CSV."""
    if df is not None and 'Email Address' in df.columns:
        return df['Email Address'].dropna().unique().tolist()
    return []

# ==========================================
# AUTHENTICATION FUNCTIONS
# ==========================================

def initialize_session_state():
    """Initialize session state variables."""
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    if 'role' not in st.session_state:
        st.session_state.role = None
    if 'user_email' not in st.session_state:
        st.session_state.user_email = None
    if 'user_name' not in st.session_state:
        st.session_state.user_name = None

def authenticate_user(email, password, df):
    """
    Authenticate user based on email and password.
    
    Authentication Logic:
    1. Check if credentials match teacher (hardcoded)
    2. For students: Check if email exists in CSV AND password matches common password
    
    Returns: tuple (success: bool, role: str, error_message: str)
    """
    email = email.strip().lower()
    
    # Teacher authentication - hardcoded credentials
    if email == TEACHER_EMAIL.lower() and password == TEACHER_PASSWORD:
        return True, "teacher", None
    
    # Student authentication
    # Check if email exists in CSV
    student_emails = [e.lower().strip() for e in df['Email Address'].dropna().tolist()]
    
    if email in student_emails:
        # Check password matches common student password
        if password == STUDENT_PASSWORD:
            return True, "student", None
        else:
            return False, None, "Invalid password. Please try again."
    
    # Check if it was an attempt to login as teacher with wrong password
    if email == TEACHER_EMAIL.lower():
        return False, None, "Invalid teacher password."
    
    return False, None, "Email not found in the survey database. Only students who participated in the survey can access this portal."

def logout():
    """Clear session state and logout user."""
    st.session_state.authenticated = False
    st.session_state.role = None
    st.session_state.user_email = None
    st.session_state.user_name = None
    st.rerun()

# ==========================================
# LOGIN PAGE
# ==========================================

def render_login_page(df):
    """Render the login page with academic styling."""
    
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>Student & Teacher Login Portal</h1>
        <p>Analyzing the Role of ChatGPT in Enhancing Programming Skills</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Center the login form
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown('<div class="login-card">', unsafe_allow_html=True)
        st.markdown('<h2>Welcome Back</h2>', unsafe_allow_html=True)
        
        # Login form
        with st.form("login_form", clear_on_submit=False):
            email = st.text_input(
                "Email Address",
                placeholder="Enter your email",
                key="login_email"
            )
            
            password = st.text_input(
                "Password",
                type="password",
                placeholder="Enter your password",
                key="login_password"
            )
            
            submit_btn = st.form_submit_button("Login", use_container_width=True)
            
            if submit_btn:
                if not email or not password:
                    st.error("Please enter both email and password.")
                else:
                    success, role, error = authenticate_user(email, password, df)
                    
                    if success:
                        st.session_state.authenticated = True
                        st.session_state.role = role
                        st.session_state.user_email = email.strip().lower()
                        
                        # Get user name from CSV if student
                        if role == "student":
                            user_row = df[df['Email Address'].str.lower().str.strip() == email.strip().lower()]
                            if not user_row.empty and 'Name' in df.columns:
                                st.session_state.user_name = user_row['Name'].values[0]
                            else:
                                st.session_state.user_name = email.split('@')[0]
                        else:
                            st.session_state.user_name = "Teacher"
                        
                        st.success(f"Welcome, {st.session_state.user_name}!")
                        st.rerun()
                    else:
                        st.error(error)
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Info box with credentials hint
        st.markdown("""
        <div class="info-box">
            <strong>Access Information:</strong><br>
            <small>
            • Students: Use your survey email + password: <code>student123</code><br>
            • Teachers: Use authorized credentials
            </small>
        </div>
        """, unsafe_allow_html=True)

# ==========================================
# VISUALIZATION FUNCTIONS
# ==========================================

def create_likert_bar_chart(data, title, color_palette='Blues_d'):
    """Create a horizontal bar chart for Likert scale responses."""
    fig, ax = plt.subplots(figsize=(10, 6))
    
    colors = sns.color_palette(color_palette, len(data))
    bars = ax.barh(range(len(data)), data.values, color=colors)
    
    ax.set_yticks(range(len(data)))
    ax.set_yticklabels([label[:50] + '...' if len(label) > 50 else label for label in data.index], fontsize=9)
    ax.set_xlabel('Average Score (1-5)', fontsize=10)
    ax.set_title(title, fontsize=12, fontweight='bold', color='#1e3a5f')
    ax.set_xlim(0, 5)
    ax.axvline(x=3, color='#e53e3e', linestyle='--', alpha=0.5, label='Neutral (3)')
    
    # Add value labels
    for bar, val in zip(bars, data.values):
        ax.text(val + 0.1, bar.get_y() + bar.get_height()/2, f'{val:.2f}', 
                va='center', fontsize=8, color='#2d3748')
    
    plt.tight_layout()
    return fig

def create_pie_chart(data, title):
    """Create a pie chart for categorical data."""
    fig, ax = plt.subplots(figsize=(8, 8))
    
    colors = sns.color_palette('Blues', len(data))
    wedges, texts, autotexts = ax.pie(
        data.values, 
        labels=data.index,
        autopct='%1.1f%%',
        colors=colors,
        startangle=90,
        explode=[0.02] * len(data)
    )
    
    ax.set_title(title, fontsize=12, fontweight='bold', color='#1e3a5f')
    plt.setp(autotexts, size=9, weight='bold')
    plt.setp(texts, size=9)
    
    return fig

def create_heatmap(df, likert_cols, title):
    """Create a correlation heatmap for Likert scale responses."""
    # Shorten column names for display
    short_names = {col: f"Q{i+1}" for i, col in enumerate(likert_cols)}
    df_corr = df[likert_cols].rename(columns=short_names)
    
    fig, ax = plt.subplots(figsize=(12, 10))
    
    correlation = df_corr.corr()
    mask = np.triu(np.ones_like(correlation, dtype=bool))
    
    sns.heatmap(
        correlation,
        mask=mask,
        annot=True,
        fmt='.2f',
        cmap='Blues',
        center=0,
        square=True,
        linewidths=0.5,
        ax=ax,
        annot_kws={'size': 8}
    )
    
    ax.set_title(title, fontsize=12, fontweight='bold', color='#1e3a5f')
    
    plt.tight_layout()
    return fig, short_names

def create_distribution_plot(df, column, title):
    """Create a distribution plot for a single Likert question."""
    fig, ax = plt.subplots(figsize=(8, 5))
    
    value_counts = df[column].value_counts().sort_index()
    colors = ['#c53030', '#ed8936', '#ecc94b', '#48bb78', '#2c5282']
    
    bars = ax.bar(value_counts.index, value_counts.values, color=colors[:len(value_counts)])
    
    ax.set_xlabel('Response (1=Strongly Disagree, 5=Strongly Agree)', fontsize=10)
    ax.set_ylabel('Number of Responses', fontsize=10)
    ax.set_title(title, fontsize=11, fontweight='bold', color='#1e3a5f')
    ax.set_xticks([1, 2, 3, 4, 5])
    
    for bar in bars:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
                f'{int(height)}', ha='center', va='bottom', fontsize=9)
    
    plt.tight_layout()
    return fig

def create_wordcloud(text, title):
    """Create a word cloud from text data."""
    if not text or text.strip() == '':
        return None
    
    wordcloud = WordCloud(
        width=800,
        height=400,
        background_color='white',
        colormap='Blues',
        max_words=100,
        min_font_size=10
    ).generate(text)
    
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.imshow(wordcloud, interpolation='bilinear')
    ax.axis('off')
    ax.set_title(title, fontsize=12, fontweight='bold', color='#1e3a5f')
    
    plt.tight_layout()
    return fig

def create_semester_comparison(df, likert_cols):
    """Create semester-wise comparison chart."""
    if 'Sem' not in df.columns:
        return None
    
    semester_means = df.groupby('Sem')[likert_cols].mean().mean(axis=1).sort_index()
    
    fig, ax = plt.subplots(figsize=(10, 5))
    
    colors = sns.color_palette('Blues', len(semester_means))
    bars = ax.bar(semester_means.index, semester_means.values, color=colors)
    
    ax.set_xlabel('Semester', fontsize=10)
    ax.set_ylabel('Average Score', fontsize=10)
    ax.set_title('Average Scores by Semester', fontsize=12, fontweight='bold', color='#1e3a5f')
    ax.set_ylim(0, 5)
    ax.axhline(y=3, color='#e53e3e', linestyle='--', alpha=0.5)
    
    for bar in bars:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                f'{height:.2f}', ha='center', va='bottom', fontsize=9)
    
    plt.tight_layout()
    return fig

def create_course_comparison(df, likert_cols):
    """Create course-wise comparison chart."""
    if 'Course' not in df.columns:
        return None
    
    # Group similar courses
    course_means = df.groupby('Course')[likert_cols].mean().mean(axis=1)
    
    # Take top 10 courses by response count
    top_courses = df['Course'].value_counts().head(10).index
    course_means = course_means[course_means.index.isin(top_courses)].sort_values(ascending=True)
    
    fig, ax = plt.subplots(figsize=(12, 6))
    
    colors = sns.color_palette('Blues', len(course_means))
    bars = ax.barh(range(len(course_means)), course_means.values, color=colors)
    
    ax.set_yticks(range(len(course_means)))
    ax.set_yticklabels([c[:30] + '...' if len(c) > 30 else c for c in course_means.index], fontsize=9)
    ax.set_xlabel('Average Score', fontsize=10)
    ax.set_title('Average Scores by Course (Top 10)', fontsize=12, fontweight='bold', color='#1e3a5f')
    ax.set_xlim(0, 5)
    ax.axvline(x=3, color='#e53e3e', linestyle='--', alpha=0.5)
    
    for bar, val in zip(bars, course_means.values):
        ax.text(val + 0.05, bar.get_y() + bar.get_height()/2, f'{val:.2f}',
                va='center', fontsize=8)
    
    plt.tight_layout()
    return fig

# ==========================================
# TEACHER DASHBOARD
# ==========================================

def render_teacher_dashboard(df, likert_cols):
    """Render the full teacher dashboard with all analytics."""
    
    # Sidebar
    with st.sidebar:
        st.markdown(f"""
        <div style='text-align: center; padding: 1rem;'>
            <h3 style='color: white;'>Teacher Dashboard</h3>
            <p style='color: #e2e8f0;'>{st.session_state.user_email}</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        if st.button("Logout", key="logout_btn", use_container_width=True):
            logout()
    
    # Main content header
    st.markdown("""
    <div class="main-header">
        <h1>Research Analytics Dashboard</h1>
        <p>Complete Analysis: ChatGPT's Impact on Programming Education</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Key metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="Total Responses",
            value=len(df),
            delta=None
        )
    
    with col2:
        avg_score = df[likert_cols].mean().mean()
        st.metric(
            label="Overall Avg Score",
            value=f"{avg_score:.2f}/5"
        )
    
    with col3:
        unique_courses = df['Course'].nunique() if 'Course' in df.columns else 0
        st.metric(
            label="Courses",
            value=unique_courses
        )
    
    with col4:
        unique_sems = df['Sem'].nunique() if 'Sem' in df.columns else 0
        st.metric(
            label="Semesters",
            value=unique_sems
        )
    
    st.markdown("---")
    
    # Tabs for different views
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "Overview", "Response Analysis", "Comparisons", "Correlations", "Raw Data"
    ])
    
    with tab1:
        st.markdown('<h3 class="section-header">Survey Overview</h3>', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Average scores for all questions
            avg_scores = df[likert_cols].mean().sort_values(ascending=True)
            fig = create_likert_bar_chart(avg_scores, "Average Scores by Question")
            st.pyplot(fig)
            plt.close()
        
        with col2:
            # Response distribution by semester
            if 'Sem' in df.columns:
                sem_counts = df['Sem'].value_counts()
                fig = create_pie_chart(sem_counts, "Responses by Semester")
                st.pyplot(fig)
                plt.close()
    
    with tab2:
        st.markdown('<h3 class="section-header">Detailed Response Analysis</h3>', unsafe_allow_html=True)
        
        # Question selector
        selected_question = st.selectbox(
            "Select a question to analyze:",
            options=likert_cols,
            key="question_selector"
        )
        
        if selected_question:
            col1, col2 = st.columns(2)
            
            with col1:
                fig = create_distribution_plot(df, selected_question, f"Response Distribution")
                st.pyplot(fig)
                plt.close()
            
            with col2:
                # Statistics
                st.markdown("**Statistics:**")
                stats = df[selected_question].describe()
                st.write(f"- Mean: {stats['mean']:.2f}")
                st.write(f"- Median: {stats['50%']:.2f}")
                st.write(f"- Std Dev: {stats['std']:.2f}")
                st.write(f"- Min: {stats['min']:.0f}")
                st.write(f"- Max: {stats['max']:.0f}")
                
                # Agreement percentage
                agree_pct = (df[selected_question] >= 4).mean() * 100
                st.write(f"- Agreement Rate (4-5): {agree_pct:.1f}%")
        
        # Top performing and bottom performing questions
        st.markdown("---")
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Top 5 Highest Rated Aspects:**")
            top_5 = df[likert_cols].mean().nlargest(5)
            for q, score in top_5.items():
                short_q = q[:60] + '...' if len(q) > 60 else q
                st.write(f"• {short_q}: **{score:.2f}**")
        
        with col2:
            st.markdown("**Top 5 Areas for Improvement:**")
            bottom_5 = df[likert_cols].mean().nsmallest(5)
            for q, score in bottom_5.items():
                short_q = q[:60] + '...' if len(q) > 60 else q
                st.write(f"• {short_q}: **{score:.2f}**")
    
    with tab3:
        st.markdown('<h3 class="section-header">Course & Semester Comparisons</h3>', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            fig = create_semester_comparison(df, likert_cols)
            if fig:
                st.pyplot(fig)
                plt.close()
        
        with col2:
            fig = create_course_comparison(df, likert_cols)
            if fig:
                st.pyplot(fig)
                plt.close()
    
    with tab4:
        st.markdown('<h3 class="section-header">Correlation Analysis</h3>', unsafe_allow_html=True)
        
        fig, legend = create_heatmap(df, likert_cols, "Correlation Matrix of Survey Questions")
        st.pyplot(fig)
        plt.close()
        
        # Legend for question numbers
        with st.expander("Question Legend"):
            for orig, short in legend.items():
                st.write(f"**{short}**: {orig}")
    
    with tab5:
        st.markdown('<h3 class="section-header">Raw Data Export</h3>', unsafe_allow_html=True)
        
        # Filter options
        col1, col2 = st.columns(2)
        with col1:
            course_filter = st.multiselect(
                "Filter by Course:",
                options=df['Course'].unique() if 'Course' in df.columns else [],
                default=[],
                key="course_filter"
            )
        with col2:
            sem_filter = st.multiselect(
                "Filter by Semester:",
                options=df['Sem'].unique() if 'Sem' in df.columns else [],
                default=[],
                key="sem_filter"
            )
        
        filtered_df = df.copy()
        if course_filter:
            filtered_df = filtered_df[filtered_df['Course'].isin(course_filter)]
        if sem_filter:
            filtered_df = filtered_df[filtered_df['Sem'].isin(sem_filter)]
        
        st.write(f"Showing {len(filtered_df)} of {len(df)} responses")
        st.dataframe(filtered_df, use_container_width=True, height=400)
        
        # Download buttons
        col1, col2 = st.columns(2)
        with col1:
            csv = filtered_df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="Download CSV",
                data=csv,
                file_name="survey_data_export.csv",
                mime="text/csv",
                use_container_width=True
            )
        
        with col2:
            # Create summary report
            summary = f"""
Research Summary Report
=======================
Total Responses: {len(df)}
Courses: {df['Course'].nunique() if 'Course' in df.columns else 'N/A'}
Semesters: {df['Sem'].nunique() if 'Sem' in df.columns else 'N/A'}

Overall Average Score: {df[likert_cols].mean().mean():.2f}/5

Top Rated Aspects:
{chr(10).join([f'- {q[:50]}...: {s:.2f}' for q, s in df[likert_cols].mean().nlargest(3).items()])}

Areas for Improvement:
{chr(10).join([f'- {q[:50]}...: {s:.2f}' for q, s in df[likert_cols].mean().nsmallest(3).items()])}
            """
            st.download_button(
                label="Download Summary",
                data=summary,
                file_name="survey_summary.txt",
                mime="text/plain",
                use_container_width=True
            )

# ==========================================
# STUDENT DASHBOARD
# ==========================================

def render_student_dashboard(df, likert_cols):
    """Render the student dashboard showing only their own data."""
    
    # Get student's data
    student_email = st.session_state.user_email
    student_data = df[df['Email Address'].str.lower().str.strip() == student_email]
    
    if student_data.empty:
        st.error("Could not find your survey responses. Please contact the administrator.")
        return
    
    student_row = student_data.iloc[0]
    
    # Sidebar
    with st.sidebar:
        st.markdown(f"""
        <div style='text-align: center; padding: 1rem;'>
            <h3 style='color: white;'>Student Portal</h3>
            <p style='color: #e2e8f0;'>{st.session_state.user_name}</p>
            <small style='color: #a0aec0;'>{student_email}</small>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Student info
        if 'Course' in df.columns:
            st.write(f"**Course:** {student_row.get('Course', 'N/A')}")
        if 'Sem' in df.columns:
            st.write(f"**Semester:** {student_row.get('Sem', 'N/A')}")
        
        st.markdown("---")
        
        if st.button("Logout", key="student_logout", use_container_width=True):
            logout()
    
    # Main content header
    st.markdown(f"""
    <div class="main-header">
        <h1>Your Survey Analysis</h1>
        <p>Welcome back, {st.session_state.user_name}!</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Tabs
    tab1, tab2, tab3 = st.tabs(["My Responses", "Compare with Class", "Insights"])
    
    with tab1:
        st.markdown('<h3 class="section-header">Your Survey Responses</h3>', unsafe_allow_html=True)
        
        # Calculate student's average
        student_scores = student_row[likert_cols].astype(float)
        student_avg = student_scores.mean()
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Your Average Score", f"{student_avg:.2f}/5")
        with col2:
            class_avg = df[likert_cols].mean().mean()
            diff = student_avg - class_avg
            st.metric("Class Average", f"{class_avg:.2f}/5", f"{diff:+.2f}")
        with col3:
            agree_count = (student_scores >= 4).sum()
            st.metric("Positive Responses (4-5)", f"{agree_count}/{len(likert_cols)}")
        
        st.markdown("---")
        
        # Display responses in a clean format
        st.markdown("**Your Detailed Responses:**")
        
        for i, col in enumerate(likert_cols, 1):
            score = student_row[col]
            score_int = int(score) if pd.notna(score) else 0
            
            # Color based on score
            if score_int >= 4:
                color = "#48bb78"  # Green
            elif score_int == 3:
                color = "#ecc94b"  # Yellow
            else:
                color = "#f56565"  # Red
            
            short_q = col[:80] + '...' if len(col) > 80 else col
            
            st.markdown(f"""
            <div style='background: #f7fafc; padding: 0.75rem; margin: 0.5rem 0; border-radius: 8px; border-left: 4px solid {color};'>
                <strong>Q{i}:</strong> {short_q}<br>
                <span style='color: {color}; font-size: 1.25rem; font-weight: bold;'>Score: {score_int}/5</span>
            </div>
            """, unsafe_allow_html=True)
    
    with tab2:
        st.markdown('<h3 class="section-header">Your Scores vs Class Average</h3>', unsafe_allow_html=True)
        
        # Create comparison chart
        fig, ax = plt.subplots(figsize=(12, 8))
        
        x = np.arange(len(likert_cols))
        width = 0.35
        
        student_vals = student_row[likert_cols].astype(float).values
        class_vals = df[likert_cols].mean().values
        
        bars1 = ax.barh(x - width/2, student_vals, width, label='Your Score', color='#2c5282')
        bars2 = ax.barh(x + width/2, class_vals, width, label='Class Average', color='#90cdf4')
        
        ax.set_xlabel('Score (1-5)', fontsize=10)
        ax.set_yticks(x)
        ax.set_yticklabels([f'Q{i+1}' for i in range(len(likert_cols))], fontsize=9)
        ax.set_xlim(0, 5.5)
        ax.legend(loc='lower right')
        ax.set_title('Your Responses vs Class Average', fontsize=12, fontweight='bold', color='#1e3a5f')
        ax.axvline(x=3, color='#e53e3e', linestyle='--', alpha=0.3)
        
        plt.tight_layout()
        st.pyplot(fig)
        plt.close()
        
        # Legend
        with st.expander("Question Legend"):
            for i, col in enumerate(likert_cols, 1):
                st.write(f"**Q{i}**: {col}")
    
    with tab3:
        st.markdown('<h3 class="section-header">Personal Insights</h3>', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Your Strongest Areas (Score 5):**")
            strong_areas = student_row[likert_cols][student_row[likert_cols] == 5]
            if len(strong_areas) > 0:
                for q in strong_areas.index[:5]:
                    short_q = q[:60] + '...' if len(q) > 60 else q
                    st.write(f"• {short_q}")
            else:
                st.write("No questions rated 5")
        
        with col2:
            st.markdown("**Areas to Explore (Score ≤ 2):**")
            weak_areas = student_row[likert_cols][student_row[likert_cols] <= 2]
            if len(weak_areas) > 0:
                for q in weak_areas.index[:5]:
                    short_q = q[:60] + '...' if len(q) > 60 else q
                    st.write(f"• {short_q}")
            else:
                st.write("No questions rated ≤ 2")
        
        # Percentile ranking
        st.markdown("---")
        st.markdown("**Your Position in Class:**")
        
        all_averages = df[likert_cols].mean(axis=1).sort_values()
        student_rank = (all_averages < student_avg).sum()
        percentile = (student_rank / len(all_averages)) * 100
        
        st.write(f"Your average score of **{student_avg:.2f}** puts you in the **{percentile:.0f}th percentile** of the class.")
        
        if percentile >= 75:
            st.success("Excellent! You have a very positive perception of ChatGPT for programming.")
        elif percentile >= 50:
            st.info("Good! Your perception is above average.")
        else:
            st.warning("Your responses indicate some reservations about ChatGPT - that's valuable feedback!")

# ==========================================
# MAIN APPLICATION
# ==========================================

def main():
    """Main application entry point."""
    
    # Apply custom styles
    apply_custom_styles()
    
    # Initialize session state
    initialize_session_state()
    
    # Load data
    df, likert_cols = load_data()
    
    if df is None:
        st.error("Failed to load survey data. Please ensure the CSV file exists.")
        return
    
    # Route based on authentication status
    if not st.session_state.authenticated:
        render_login_page(df)
    else:
        # Role-based dashboard rendering
        if st.session_state.role == "teacher":
            render_teacher_dashboard(df, likert_cols)
        elif st.session_state.role == "student":
            render_student_dashboard(df, likert_cols)

if __name__ == "__main__":
    main()
