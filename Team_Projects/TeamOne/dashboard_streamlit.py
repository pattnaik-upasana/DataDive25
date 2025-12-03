"""
Streamlit Dashboard for Job Creation Analysis

Run with: streamlit run dashboard_streamlit.py
"""

import streamlit as st
import duckdb
import pandas as pd
import altair as alt
from pathlib import Path

# Page config
st.set_page_config(
    page_title="Job Creation Analysis Dashboard",
    page_icon="📊",
    layout="wide"
)

# Configure Altair
alt.data_transformers.disable_max_rows()

# Paths
DATA_DIR = Path(__file__).parent / "data"
DB_PATH = DATA_DIR / "joined_data.duckdb"

# Title
st.title("📊 Job Creation Analysis Dashboard")
st.markdown("Analysis based on research questions from firm performance indicators")

# Connect to database
@st.cache_resource
def get_connection():
    return duckdb.connect(str(DB_PATH))

conn = get_connection()

# Sidebar for navigation
st.sidebar.title("Navigation")
page = st.sidebar.radio(
    "Select Analysis",
    [
        "Overview",
        "1. Job Creation by Company Size",
        "2. Firm Maturity & Job Creation",
        "3. Access to Credit & Job Creation",
        "4. Interest Rates & Job Creation",
        "5. Industry Employment Across Countries",
        "6. Regulatory Burden & Gender",
        "7. Management Quality vs Finance",
        "Data Explorer"
    ]
)

# Get column information
@st.cache_data
def get_columns():
    return conn.execute("DESCRIBE joined_data").df()

columns_df = get_columns()

# Helper function to find columns
def find_columns(keywords):
    """Find columns matching keywords"""
    matches = []
    for col in columns_df['column_name']:
        col_lower = col.lower()
        if any(kw.lower() in col_lower for kw in keywords):
            matches.append(col)
    return matches

# Overview page
if page == "Overview":
    st.header("Overview")
    
    # Get basic stats
    total_rows = conn.execute("SELECT COUNT(*) FROM joined_data").fetchone()[0]
    total_cols = len(columns_df)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Firms", f"{total_rows:,}")
    with col2:
        st.metric("Total Variables", total_cols)
    with col3:
        st.metric("Database", "DuckDB")
    
    st.markdown("---")
    st.subheader("Research Questions Summary")
    
    st.markdown("""
    This dashboard explores the following research questions:
    
    1. **Job Creation Model**: What factors predict job creation?
       - Company size (absolute and size-adjusted)
       - Access to credit
       - Certification
       - Interest rates
    
    2. **Firm Maturity**: How does firm maturity affect jobs?
       - Newer firms create more jobs
       - Negative correlation with maturity
    
    3. **Access to Credit**: Impact on job creation ability
    
    4. **Interest Rates**: Relationship with job creation
    
    5. **Industry Employment**: Correlation across countries
    
    6. **Regulatory Burden & Gender**: Differential impact on female-led firms
    
    7. **Management Quality vs Finance**: Which is a stronger predictor?
    """)
    
    st.markdown("---")
    st.subheader("Available Columns")
    st.dataframe(columns_df, use_container_width=True)

# Job Creation by Company Size
elif page == "1. Job Creation by Company Size":
    st.header("Job Creation by Company Size")
    
    # Find relevant columns
    size_cols = find_columns(['size', 'siz', 'employee', 'emp_num'])
    job_cols = find_columns(['job', 'emp', 'worker', 'employment'])
    
    if not size_cols or not job_cols:
        st.warning("Could not find size or job-related columns. Please check the database.")
        st.write("Size columns found:", size_cols)
        st.write("Job columns found:", job_cols)
    else:
        col1, col2 = st.columns(2)
        with col1:
            size_col = st.selectbox("Select Size Column", size_cols)
        with col2:
            job_col = st.selectbox("Select Job/Employment Column", job_cols)
        
        # Absolute terms
        st.subheader("Absolute Job Creation by Company Size")
        query1 = f"""
            SELECT 
                CASE 
                    WHEN {size_col} < 20 THEN 'Small'
                    WHEN {size_col} < 100 THEN 'Medium'
                    ELSE 'Large'
                END AS company_size,
                COUNT(*) AS firm_count,
                SUM({job_col}) AS total_jobs_created,
                AVG({job_col}) AS avg_jobs_per_firm
            FROM joined_data
            WHERE {size_col} IS NOT NULL 
              AND {job_col} IS NOT NULL
            GROUP BY company_size
            ORDER BY 
                CASE company_size
                    WHEN 'Small' THEN 1
                    WHEN 'Medium' THEN 2
                    WHEN 'Large' THEN 3
                END
        """
        
        try:
            df1 = conn.execute(query1).df()
            if not df1.empty:
                chart1 = alt.Chart(df1).mark_bar().encode(
                    x=alt.X('company_size', title='Company Size'),
                    y=alt.Y('total_jobs_created', title='Total Jobs Created'),
                    color='company_size',
                    tooltip=['company_size', 'total_jobs_created', 'firm_count']
                ).properties(width=600, height=400)
                st.altair_chart(chart1, use_container_width=True)
                st.dataframe(df1)
            else:
                st.info("No data available for this combination.")
        except Exception as e:
            st.error(f"Error: {e}")
        
        # Size-adjusted terms
        st.subheader("Size-Adjusted Job Creation (Jobs per Size Unit)")
        query2 = f"""
            SELECT 
                CASE 
                    WHEN {size_col} < 20 THEN 'Small'
                    WHEN {size_col} < 100 THEN 'Medium'
                    ELSE 'Large'
                END AS company_size,
                COUNT(*) AS firm_count,
                AVG({job_col} / NULLIF({size_col}, 0)) AS jobs_per_size_unit,
                AVG({job_col}) AS avg_jobs_per_firm
            FROM joined_data
            WHERE {size_col} IS NOT NULL 
              AND {job_col} IS NOT NULL
              AND {size_col} > 0
            GROUP BY company_size
            ORDER BY 
                CASE company_size
                    WHEN 'Small' THEN 1
                    WHEN 'Medium' THEN 2
                    WHEN 'Large' THEN 3
                END
        """
        
        try:
            df2 = conn.execute(query2).df()
            if not df2.empty:
                chart2 = alt.Chart(df2).mark_bar().encode(
                    x=alt.X('company_size', title='Company Size'),
                    y=alt.Y('jobs_per_size_unit', title='Jobs per Size Unit'),
                    color='company_size',
                    tooltip=['company_size', 'jobs_per_size_unit', 'firm_count']
                ).properties(width=600, height=400)
                st.altair_chart(chart2, use_container_width=True)
                st.dataframe(df2)
        except Exception as e:
            st.error(f"Error: {e}")

# Firm Maturity
elif page == "2. Firm Maturity & Job Creation":
    st.header("Firm Maturity and Job Creation")
    
    maturity_cols = find_columns(['age', 'mature', 'old', 'young', 'year', 'establish', 'founded'])
    job_cols = find_columns(['job', 'emp', 'worker', 'employment'])
    
    if not maturity_cols or not job_cols:
        st.warning("Could not find maturity or job-related columns.")
    else:
        col1, col2 = st.columns(2)
        with col1:
            maturity_col = st.selectbox("Select Maturity/Age Column", maturity_cols)
        with col2:
            job_col = st.selectbox("Select Job/Employment Column", job_cols)
        
        query = f"""
            SELECT 
                CASE 
                    WHEN {maturity_col} < 5 THEN 'Very Young (<5 years)'
                    WHEN {maturity_col} < 10 THEN 'Young (5-10 years)'
                    WHEN {maturity_col} < 20 THEN 'Mature (10-20 years)'
                    ELSE 'Old (>20 years)'
                END AS firm_age_category,
                COUNT(*) AS firm_count,
                AVG({job_col}) AS avg_jobs_created
            FROM joined_data
            WHERE {maturity_col} IS NOT NULL 
              AND {job_col} IS NOT NULL
            GROUP BY firm_age_category
            ORDER BY 
                CASE firm_age_category
                    WHEN 'Very Young (<5 years)' THEN 1
                    WHEN 'Young (5-10 years)' THEN 2
                    WHEN 'Mature (10-20 years)' THEN 3
                    WHEN 'Old (>20 years)' THEN 4
                END
        """
        
        try:
            df = conn.execute(query).df()
            if not df.empty:
                chart = alt.Chart(df).mark_bar().encode(
                    x=alt.X('firm_age_category', title='Firm Age Category'),
                    y=alt.Y('avg_jobs_created', title='Average Jobs Created'),
                    color='firm_age_category',
                    tooltip=['firm_age_category', 'avg_jobs_created', 'firm_count']
                ).properties(width=600, height=400)
                st.altair_chart(chart, use_container_width=True)
                st.dataframe(df)
            else:
                st.info("No data available.")
        except Exception as e:
            st.error(f"Error: {e}")

# Access to Credit
elif page == "3. Access to Credit & Job Creation":
    st.header("Access to Credit and Job Creation")
    
    credit_cols = find_columns(['credit', 'loan', 'finance', 'lending', 'line'])
    job_cols = find_columns(['job', 'emp', 'worker', 'employment'])
    
    if not credit_cols or not job_cols:
        st.warning("Could not find credit or job-related columns.")
    else:
        col1, col2 = st.columns(2)
        with col1:
            credit_col = st.selectbox("Select Credit/Finance Column", credit_cols)
        with col2:
            job_col = st.selectbox("Select Job/Employment Column", job_cols)
        
        query = f"""
            SELECT 
                {credit_col} AS credit_access,
                COUNT(*) AS firm_count,
                AVG({job_col}) AS avg_jobs_created
            FROM joined_data
            WHERE {credit_col} IS NOT NULL 
              AND {job_col} IS NOT NULL
            GROUP BY {credit_col}
            ORDER BY avg_jobs_created DESC
            LIMIT 20
        """
        
        try:
            df = conn.execute(query).df()
            if not df.empty:
                chart = alt.Chart(df).mark_bar().encode(
                    x=alt.X('credit_access', title='Credit Access Category'),
                    y=alt.Y('avg_jobs_created', title='Average Jobs Created'),
                    color='credit_access',
                    tooltip=['credit_access', 'avg_jobs_created', 'firm_count']
                ).properties(width=600, height=400)
                st.altair_chart(chart, use_container_width=True)
                st.dataframe(df)
        except Exception as e:
            st.error(f"Error: {e}")

# Interest Rates
elif page == "4. Interest Rates & Job Creation":
    st.header("Interest Rates and Job Creation")
    
    interest_cols = find_columns(['interest', 'rate', 'financing'])
    job_cols = find_columns(['job', 'emp', 'worker', 'employment'])
    
    if not interest_cols or not job_cols:
        st.warning("Could not find interest rate or job-related columns.")
    else:
        col1, col2 = st.columns(2)
        with col1:
            interest_col = st.selectbox("Select Interest Rate Column", interest_cols)
        with col2:
            job_col = st.selectbox("Select Job/Employment Column", job_cols)
        
        query = f"""
            SELECT 
                {interest_col} AS interest_rate_category,
                COUNT(*) AS firm_count,
                AVG({job_col}) AS avg_jobs_created,
                SUM(CASE WHEN {job_col} < 0 THEN 1 ELSE 0 END) AS firms_with_job_loss
            FROM joined_data
            WHERE {interest_col} IS NOT NULL 
              AND {job_col} IS NOT NULL
            GROUP BY {interest_col}
            ORDER BY avg_jobs_created DESC
            LIMIT 20
        """
        
        try:
            df = conn.execute(query).df()
            if not df.empty:
                chart = alt.Chart(df).mark_bar().encode(
                    x=alt.X('interest_rate_category', title='Interest Rate Category'),
                    y=alt.Y('avg_jobs_created', title='Average Jobs Created'),
                    color='interest_rate_category',
                    tooltip=['interest_rate_category', 'avg_jobs_created', 'firm_count', 'firms_with_job_loss']
                ).properties(width=600, height=400)
                st.altair_chart(chart, use_container_width=True)
                st.dataframe(df)
        except Exception as e:
            st.error(f"Error: {e}")

# Data Explorer
elif page == "Data Explorer":
    st.header("Data Explorer")
    
    st.subheader("Run Custom SQL Queries")
    
    query = st.text_area("Enter SQL Query", height=200, value="SELECT * FROM joined_data LIMIT 100")
    
    if st.button("Execute Query"):
        try:
            result = conn.execute(query).df()
            st.dataframe(result, use_container_width=True)
            st.success(f"Query returned {len(result)} rows")
        except Exception as e:
            st.error(f"Error: {e}")
    
    st.subheader("Available Columns")
    st.dataframe(columns_df, use_container_width=True)

# Placeholder pages for other questions
else:
    st.header(page)
    st.info("This analysis is coming soon. Use the Data Explorer to create custom visualizations.")

