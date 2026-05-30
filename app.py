import os
import psycopg2
import streamlit as st
import pandas as pd
from dotenv import load_dotenv

# Page configuration
st.set_page_config(page_title="Technical PM 3D Matrix Dashboard", page_icon="📊", layout="wide")

# Force load and sanitize configurations
load_dotenv(override=True)
db_url = os.getenv("DATABASE_URL", "").strip().strip('"').strip("'")

@st.cache_data(ttl=30) # Caches data for fast clicks
def load_data_from_neon():
    # 🚀 Updated to select the updated plural Array columns from your v1.1 DB table
    query = """
    SELECT title, company, url, functional_domains, audience_scopes, technical_depth_profiles, ai_confidence, listing_depth 
    FROM job_listings 
    ORDER BY id DESC;
    """
    try:
        conn = psycopg2.connect(db_url)
        df = pd.read_sql_query(query, conn)
        conn.close()
        return df
    except Exception as e:
        st.error(f"Failed to connect to Neon: {e}")
        return pd.DataFrame()

# Helper function to check if any item in a database list matches user multi-select sidebar filters
def matches_array_filters(row_list, selected_filters):
    if not row_list: 
        return False
    # Handles both native python lists and raw string representations that might arrive from SQL
    actual_list = row_list if isinstance(row_list, list) else list(row_list)
    return any(item in selected_filters for item in actual_list)

# Main Header
st.title("PM 3D Taxonomy Matrix Dashboard")
st.markdown("Live multi-dimensional structured metadata parsed straight from corporate applicant streams via OpenAI & Neon PostgreSQL.")

# Fetch Data FIRST
df = load_data_from_neon()

if df.empty:
    st.warning("No records found in the database. Ensure you ran 'python reset_db.py' and 'python crawler.py' to populate the upgraded schema tables!")
else:
    # 🎛️ Dynamic UI Filtering Sidebar Setup
    st.sidebar.header("🎯 Filter the 3D Matrix")
    
    # Explode and extract unique options from arrays to construct dynamic sidebar lists
    all_domains = sorted(list(set([item for sublist in df['functional_domains'].dropna() for item in sublist])))
    all_scopes = sorted(list(set([item for sublist in df['audience_scopes'].dropna() for item in sublist])))
    all_depths = sorted(list(set([item for sublist in df['technical_depth_profiles'].dropna() for item in sublist])))

    selected_domain = st.sidebar.multiselect("Axis 1: Functional Domain", options=all_domains, default=all_domains)
    selected_scope = st.sidebar.multiselect("Axis 2: Audience Scope", options=all_scopes, default=all_scopes)
    selected_depth = st.sidebar.multiselect("Axis 3: Technical Depth Profile", options=all_depths, default=all_depths)

    # Apply active UI state filter arrays using row intersection mapping 🚀
    filtered_df = df[
        df['functional_domains'].apply(lambda x: matches_array_filters(x, selected_domain)) &
        df['audience_scopes'].apply(lambda x: matches_array_filters(x, selected_scope)) &
        df['technical_depth_profiles'].apply(lambda x: matches_array_filters(x, selected_depth))
    ]

    # 🏛️ Metrics Topbar
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Extracted Records", len(df))
    with col2:
        # Check intersections specifically for your infrastructure and core transaction priorities
        core_tech_count = len(df[df['functional_domains'].apply(lambda x: matches_array_filters(x, ['Core Infrastructure & Platform', 'Fintech & Core Transactions', 'Data, AI & Analytics']))])
        st.metric("Core Tech & Infra Focuses", core_tech_count)
    with col3:
        raw_avg = df['ai_confidence'].mean()
        display_avg = int(raw_avg * 100) if raw_avg <= 1.0 else int(raw_avg)
        st.metric("Avg AI Model Confidence", f"{display_avg}%")

    st.markdown("---")

    # 📈 Layout Views: Primary Depth Stream Separators
    tab1, tab2 = st.tabs(["⚡ Direct Application Vacancies", "🏢 Target Company Careers Hubs"])

    with tab1:
        st.subheader("Direct-Link Job Applications")
        direct_df = filtered_df[filtered_df['listing_depth'] != 'Company Careers Board Hub'].copy()
        
        if not direct_df.empty:
            # Join lists with commas for display
            display_direct = direct_df.copy()
            display_direct['domains_list'] = display_direct['functional_domains'].apply(lambda x: ", ".join(x) if isinstance(x, list) else str(x))
            display_direct['depth_list'] = display_direct['technical_depth_profiles'].apply(lambda x: ", ".join(x) if isinstance(x, list) else str(x))
            
            st.dataframe(
                display_direct[['title', 'company', 'domains_list', 'depth_list', 'url']],
                column_config={
                    "title": "Job Title",
                    "company": "Company",
                    "domains_list": "Matched Domains",
                    "depth_list": "Technical Profile",
                    "url": st.column_config.LinkColumn("Application Link")
                },
                hide_index=True,
                use_container_width=True
            )
        else:
            st.info("No matching direct vacancy links found under active sidebar filters.")

    with tab2:
        st.subheader("Monitored Corporate Talent Hubs")
        hub_df = filtered_df[filtered_df['listing_depth'] == 'Company Careers Board Hub'].copy()
        
        if not hub_df.empty:
            display_hub = hub_df.copy()
            display_hub['domains_list'] = display_hub['functional_domains'].apply(lambda x: ", ".join(x) if isinstance(x, list) else str(x))
            
            st.dataframe(
                display_hub[['title', 'company', 'domains_list', 'url']],
                column_config={
                    "title": "Hub Label",
                    "company": "Company Hub",
                    "domains_list": "Primary Domain Mix",
                    "url": st.column_config.LinkColumn("Careers Page Link")
                },
                hide_index=True,
                use_container_width=True
            )
        else:
            st.info("No corporate career boards match your active sidebar filters.")

    st.markdown("---")

    # 📊 Aggregations Chart Tab
    st.subheader("Functional Domain Concentration Breakdown")
    if not filtered_df.empty:
        # Explode the list array rows to run counting aggregations on individual items 
        exploded_domains = filtered_df.explode('functional_domains')
        domain_counts = exploded_domains['functional_domains'].value_counts()
        st.bar_chart(domain_counts)
    else:
        st.info("No matrix data available to graph for current selections.")