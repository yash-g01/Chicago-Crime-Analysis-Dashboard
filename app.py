"""
Chicago Crimes Analysis Dashboard
Implements all requirements from the Chicago Crimes Competition Handout:
- 8 KPI Cards (Section A: K1 - K8)
- 10 Visuals (Section B: Q1 - Q10)
- Calculated columns: Month Start, Day of Week, Time of Day, Season, Crime Category
- Interactive Filters (Primary Type, Police District, Interactive Mode Toggle)
"""

import os
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# ---------------------------------------------------------
# Page Configuration
# ---------------------------------------------------------
st.set_page_config(
    page_title="Chicago Crimes Dashboard",
    page_icon="🚨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling for KPI Cards & Metric Containers
st.markdown("""
<style>
    .metric-card {
        background-color: #f8f9fa;
        border-radius: 8px;
        padding: 14px 16px;
        border-left: 4px solid #1f77b4;
        box-shadow: 0 1px 3px rgba(0,0,0,0.08);
        margin-bottom: 12px;
    }
    .metric-label {
        font-size: 0.82rem;
        color: #555555;
        font-weight: 600;
        text-transform: uppercase;
        margin-bottom: 4px;
    }
    .metric-value {
        font-size: 1.55rem;
        font-weight: 700;
        color: #111827;
    }
    .metric-sub {
        font-size: 0.75rem;
        color: #888888;
        margin-top: 2px;
    }
    .callout-box {
        background-color: #eff6ff;
        border: 1px solid #bfdbfe;
        border-radius: 6px;
        padding: 12px 16px;
        font-size: 0.88rem;
        color: #1e3a8a;
        margin-bottom: 20px;
    }
</style>
""", unsafe_allow_html=True)


# ---------------------------------------------------------
# Data Preprocessing & Feature Engineering
# ---------------------------------------------------------
VIOLENT_CRIMES = {
    'ASSAULT', 'BATTERY', 'ROBBERY', 'HOMICIDE', 
    'CRIM SEXUAL ASSAULT', 'CRIMINAL SEXUAL ASSAULT', 'KIDNAPPING'
}

PROPERTY_CRIMES = {
    'THEFT', 'BURGLARY', 'MOTOR VEHICLE THEFT', 
    'CRIMINAL DAMAGE', 'ARSON'
}

def classify_crime_category(primary_type: str) -> str:
    """Classifies crime into Violent, Property, or Other as defined in the handout."""
    if not isinstance(primary_type, str):
        return 'Other crime'
    pt_upper = primary_type.strip().upper()
    if pt_upper in VIOLENT_CRIMES:
        return 'Violent crime'
    elif pt_upper in PROPERTY_CRIMES:
        return 'Property crime'
    return 'Other crime'

def get_time_of_day(hour: int) -> str:
    """Assigns Time of Day according to the handout definitions."""
    if 0 <= hour < 6:
        return 'Night'
    elif 6 <= hour < 12:
        return 'Morning'
    elif 12 <= hour < 18:
        return 'Afternoon'
    else:
        return 'Evening'

def get_season(month: int) -> str:
    """Assigns Season according to the handout definitions."""
    if month in (12, 1, 2):
        return 'Winter'
    elif month in (3, 4, 5):
        return 'Spring'
    elif month in (6, 7, 8):
        return 'Summer'
    else:
        return 'Fall'

@st.cache_data(show_spinner="Loading and preparing crime records...")
def load_and_preprocess_data(file_source):
    """Loads CSV or Excel data and computes all required columns."""
    if isinstance(file_source, str):
        if file_source.endswith('.csv'):
            df = pd.read_csv(file_source)
        else:
            df = pd.read_excel(file_source)
    else:
        # Uploaded file object
        if file_source.name.endswith('.csv'):
            df = pd.read_csv(file_source)
        else:
            df = pd.read_excel(file_source)

    # Standardize column names (strip whitespace)
    df.columns = [col.strip() for col in df.columns]

    # Convert Date column to datetime
    if 'Date' in df.columns:
        df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
    else:
        st.error("Missing required 'Date' column in the dataset.")
        st.stop()

    # Drop rows where Date is invalid
    df = df.dropna(subset=['Date'])

    # Standardize Boolean fields
    for bool_col in ['Arrest', 'Domestic']:
        if bool_col in df.columns:
            df[bool_col] = df[bool_col].astype(str).str.strip().str.upper().isin(['TRUE', '1', 'T', 'YES'])
        else:
            df[bool_col] = False

    # Standardize Primary Type
    if 'Primary Type' in df.columns:
        df['Primary Type'] = df['Primary Type'].astype(str).str.strip().str.upper()
    else:
        df['Primary Type'] = 'UNKNOWN'

    # Extract Date components
    df['Year'] = df['Date'].dt.year
    df['Month'] = df['Date'].dt.month
    df['Hour'] = df['Date'].dt.hour
    df['Day of Week'] = df['Date'].dt.day_name()
    df['Month Start'] = df['Date'].dt.to_period('M').dt.to_timestamp()

    # Calculated columns defined in the handout
    df['Time of Day'] = df['Hour'].apply(get_time_of_day)
    df['Season'] = df['Month'].apply(get_season)
    df['Crime Category'] = df['Primary Type'].apply(classify_crime_category)

    # Standardize District column
    if 'District' in df.columns:
        df['District'] = df['District'].fillna(-1).astype(int).astype(str).replace('-1', 'Unknown')
    else:
        df['District'] = 'Unknown'

    return df


# ---------------------------------------------------------
# Sidebar: File Loading & Filters
# ---------------------------------------------------------
st.sidebar.title("🛠️ Controls & Filters")

# Default file candidate paths
default_files = [
    "Google Drive Crime Dataset.xlsx",
    "Crimes Dataset Clean.csv",
    "Crimes_Dataset_Clean.csv",
    "Crime Dataset.xlsx"
]
found_default = next((f for f in default_files if os.path.exists(f)), None)

uploaded_file = st.sidebar.file_uploader(
    "Upload Crime Dataset (.xlsx or .csv)",
    type=["xlsx", "xls", "csv"],
    help="Upload your Excel or CSV crime dataset."
)

data_source = uploaded_file if uploaded_file is not None else found_default

if data_source is None:
    st.info("👋 Please upload the **Crime Dataset (.xlsx / .csv)** in the sidebar to populate the dashboard.")
    st.stop()

# Load data
df = load_and_preprocess_data(data_source)

# Ground Rules Filter Mode Toggle
filter_mode = st.sidebar.radio(
    "Filter Application Mode:",
    options=["Interactive Sliced View", "Competition Baseline View"],
    index=0,
    help="Competition Baseline View adheres to Ground Rule 3: Use the whole dataset for all charts unless a specific period is stated."
)

# Filters (Primary Type & Police District)
all_types = sorted(df['Primary Type'].unique().tolist())
selected_types = st.sidebar.multiselect("Filter Primary Crime Type:", options=all_types, default=[])

all_districts = sorted([d for d in df['District'].unique() if d != 'Unknown'], key=lambda x: int(x) if x.isdigit() else 9999)
selected_districts = st.sidebar.multiselect("Filter Police District:", options=all_districts, default=[])

# Apply filters when in Interactive Sliced View
if filter_mode == "Interactive Sliced View":
    active_df = df.copy()
    if selected_types:
        active_df = active_df[active_df['Primary Type'].isin(selected_types)]
    if selected_districts:
        active_df = active_df[active_df['District'].isin(selected_districts)]
else:
    active_df = df  # Baseline full dataset view


# ---------------------------------------------------------
# Main Page Header & Assumptions Box
# ---------------------------------------------------------
st.title("Chicago Crimes Analysis Dashboard")
st.caption(f"Analyzing {len(active_df):,} crime records • Single-page executive view")

# ---------------------------------------------------------
# Section A: 8 KPI Cards
# ---------------------------------------------------------
# K1: Total Crimes
k1_total = len(active_df)

# K2: Arrest Rate %
k2_arrest_rate = (active_df['Arrest'].sum() / k1_total * 100) if k1_total > 0 else 0.0

# K3: Domestic Crime %
k3_domestic_rate = (active_df['Domestic'].sum() / k1_total * 100) if k1_total > 0 else 0.0

# K4: Number of different crime types
k4_unique_types = active_df['Primary Type'].nunique()

# type_arrest_true = len(active_df.query("`Primary Type` == 'THEFT' and Arrest == True"))

# st.metric(
#    label="Theft Arrests",
#    value=f"{type_arrest_true:,}",
#    delta_color="off"  # Keeps delta text neutral instead of green/red
#)

# K5: Number of crimes in the year 2016
k5_crimes_2016 = (active_df['Year'] == 2016).sum()

# K6: Average monthly crimes (April 2015 to July 2017)
period_df = active_df[(active_df['Month Start'] >= '2015-04-01') & (active_df['Month Start'] <= '2017-07-01')]
monthly_counts = period_df.groupby('Month Start').size()
k6_avg_monthly = monthly_counts.mean() if not monthly_counts.empty else 0.0

# K7: Night-time crime %
k7_night_rate = ((active_df['Time of Day'] == 'Night').sum() / k1_total * 100) if k1_total > 0 else 0.0

# K8: Violent crime %
k8_violent_rate = ((active_df['Crime Category'] == 'Violent crime').sum() / k1_total * 100) if k1_total > 0 else 0.0

st.subheader("Key Performance Indicators (Section A)")

# Render KPIs across two rows of 4 columns
kpi_cols_row1 = st.columns(4)
with kpi_cols_row1[0]:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">K1. Total Crimes</div>
        <div class="metric-value">{k1_total:,}</div>
        <div class="metric-sub">Total recorded rows</div>
    </div>
    """, unsafe_allow_html=True)

with kpi_cols_row1[1]:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">K2. Arrest Rate</div>
        <div class="metric-value">{k2_arrest_rate:.1f}%</div>
        <div class="metric-sub">{active_df['Arrest'].sum():,} arrests made</div>
    </div>
    """, unsafe_allow_html=True)

with kpi_cols_row1[2]:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">K3. Domestic Crime %</div>
        <div class="metric-value">{k3_domestic_rate:.1f}%</div>
        <div class="metric-sub">{active_df['Domestic'].sum():,} domestic incidents</div>
    </div>
    """, unsafe_allow_html=True)

with kpi_cols_row1[3]:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">K4. Crime Types</div>
        <div class="metric-value">{k4_unique_types}</div>
        <div class="metric-sub">Distinct primary types</div>
    </div>
    """, unsafe_allow_html=True)

kpi_cols_row2 = st.columns(4)
with kpi_cols_row2[0]:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">K5. Crimes in 2016</div>
        <div class="metric-value">{k5_crimes_2016:,}</div>
        <div class="metric-sub">Calendar year 2016</div>
    </div>
    """, unsafe_allow_html=True)

with kpi_cols_row2[1]:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">K6. Monthly Avg (Apr '15 - Jul '17)</div>
        <div class="metric-value">{k6_avg_monthly:,.0f}</div>
        <div class="metric-sub">Across 28 month window</div>
    </div>
    """, unsafe_allow_html=True)

with kpi_cols_row2[2]:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">K7. Night-Time Crime %</div>
        <div class="metric-value">{k7_night_rate:.1f}%</div>
        <div class="metric-sub">Hours 00:00 - 05:59</div>
    </div>
    """, unsafe_allow_html=True)

with kpi_cols_row2[3]:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">K8. Violent Crime %</div>
        <div class="metric-value">{k8_violent_rate:.1f}%</div>
        <div class="metric-sub">Assault, robbery, homicide, etc.</div>
    </div>
    """, unsafe_allow_html=True)

st.divider()


# ---------------------------------------------------------
# Section B: Visuals (10 Questions)
# ---------------------------------------------------------
st.subheader("Visual Analytics (Section B)")

# Tabbed Layout for Visuals
tab_time, tab_types, tab_location = st.tabs([
    "🕒 Time Patterns (Q1 - Q4)",
    "📊 Crime Types & Shares (Q5 - Q8)",
    "🗺️ Districts & Matrix Heatmap (Q9 - Q10)"
])

# ---------------------------------------------------------
# Tab 1: Time Patterns (Q1 - Q4)
# ---------------------------------------------------------
with tab_time:
    col_q1, col_q2 = st.columns(2)

    # Q1: Monthly Crime Count (Apr 2015 to Jul 2017)
    with col_q1:
        q1_data = (
            active_df[(active_df['Month Start'] >= '2015-04-01') & (active_df['Month Start'] <= '2017-07-01')]
            .groupby('Month Start')
            .size()
            .reset_index(name='Number of crimes')
            .sort_values('Month Start')
        )
        q1_data['Month Label'] = q1_data['Month Start'].dt.strftime('%b %y')

        fig_q1 = px.line(
            q1_data,
            x='Month Label',
            y='Number of crimes',
            markers=True,
            title="Q1. Monthly Crime Count (Apr 2015 - Jul 2017)",
            labels={'Month Label': 'Month', 'Number of crimes': 'Number of crimes'}
        )
        fig_q1.update_traces(line=dict(color='#1f77b4', width=2.5), marker=dict(size=6))
        fig_q1.update_layout(xaxis_tickangle=-45, height=360, margin=dict(l=20, r=20, t=50, b=40))
        st.plotly_chart(fig_q1, use_container_width=True)

    # Q2: Crimes by Day of the Week (Monday to Sunday)
    with col_q2:
        day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        q2_data = active_df['Day of Week'].value_counts().reindex(day_order).reset_index()
        q2_data.columns = ['Day of Week', 'Number of crimes']

        fig_q2 = px.bar(
            q2_data,
            x='Day of Week',
            y='Number of crimes',
            text='Number of crimes',
            title="Q2. Number of Crimes by Day of the Week",
            labels={'Day of Week': 'Day of Week', 'Number of crimes': 'Number of crimes'},
            color_discrete_sequence=['#4338ca']
        )
        fig_q2.update_traces(texttemplate='%{text:,.0f}', textposition='outside')
        fig_q2.update_layout(height=360, margin=dict(l=20, r=20, t=50, b=40))
        st.plotly_chart(fig_q2, use_container_width=True)

    col_q3, col_q4 = st.columns(2)

    # Q3: Crimes by Time of Day
    with col_q3:
        tod_order = ['Night', 'Morning', 'Afternoon', 'Evening']
        q3_data = active_df['Time of Day'].value_counts().reindex(tod_order).reset_index()
        q3_data.columns = ['Time of Day', 'Number of crimes']

        fig_q3 = px.bar(
            q3_data,
            x='Time of Day',
            y='Number of crimes',
            text='Number of crimes',
            title="Q3. Crimes by Time of Day (Chronological Order)",
            labels={'Time of Day': 'Time of Day', 'Number of crimes': 'Number of crimes'},
            color_discrete_sequence=['#0284c7']
        )
        fig_q3.update_traces(texttemplate='%{text:,.0f}', textposition='outside')
        fig_q3.update_layout(height=360, margin=dict(l=20, r=20, t=50, b=40))
        st.plotly_chart(fig_q3, use_container_width=True)

    # Q4: Crimes by Season for the Year 2016 only
    with col_q4:
        season_order = ['Winter', 'Spring', 'Summer', 'Fall']
        df_2016 = active_df[active_df['Year'] == 2016]
        q4_data = df_2016['Season'].value_counts().reindex(season_order).reset_index()
        q4_data.columns = ['Season', 'Number of crimes']

        fig_q4 = px.pie(
            q4_data,
            names='Season',
            values='Number of crimes',
            hole=0.45,
            title="Q4. Crimes by Season (Year 2016 Only)",
            color='Season',
            color_discrete_map={
                'Winter': '#60a5fa',
                'Spring': '#34d399',
                'Summer': '#f87171',
                'Fall': '#fbbf24'
            }
        )
        fig_q4.update_traces(textinfo='label+percent', textposition='inside')
        fig_q4.update_layout(height=360, margin=dict(l=20, r=20, t=50, b=40))
        st.plotly_chart(fig_q4, use_container_width=True)


# ---------------------------------------------------------
# Tab 2: Crime Types & Shares (Q5 - Q8)
# ---------------------------------------------------------
with tab_types:
    col_q5, col_q6 = st.columns(2)

    # Q5: Share of Violent, Property and Other crimes (donut chart)
    with col_q5:
        q5_data = active_df['Crime Category'].value_counts().reset_index()
        q5_data.columns = ['Category', 'Count']

        fig_q5 = px.pie(
            q5_data,
            names='Category',
            values='Count',
            hole=0.5,
            title="Q5. Share of Crime Categories (Violent, Property, Other)",
            color='Category',
            color_discrete_map={
                'Violent crime': '#ef4444',
                'Property crime': '#3b82f6',
                'Other crime': '#9ca3af'
            }
        )
        fig_q5.update_traces(textinfo='label+percent', textposition='inside')
        fig_q5.update_layout(height=360, margin=dict(l=20, r=20, t=50, b=40))
        st.plotly_chart(fig_q5, use_container_width=True)

    # Q6: Arrest rate % for each Time of Day (column chart)
    with col_q6:
        tod_order = ['Night', 'Morning', 'Afternoon', 'Evening']
        q6_grouped = (
            active_df.groupby('Time of Day')['Arrest']
            .agg(Total='count', Arrests='sum')
            .reindex(tod_order)
            .reset_index()
        )
        q6_grouped['Arrest Rate %'] = (q6_grouped['Arrests'] / q6_grouped['Total'] * 100).round(1)

        fig_q6 = px.bar(
            q6_grouped,
            x='Time of Day',
            y='Arrest Rate %',
            text='Arrest Rate %',
            title="Q6. Arrest Rate % for each Time of Day",
            labels={'Time of Day': 'Time of Day', 'Arrest Rate %': 'Arrest Rate (%)'},
            color_discrete_sequence=['#0d9488']
        )
        fig_q6.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
        fig_q6.update_layout(yaxis=dict(ticksuffix="%"), height=360, margin=dict(l=20, r=20, t=50, b=40))
        st.plotly_chart(fig_q6, use_container_width=True)

    col_q7, col_q8 = st.columns(2)

    # Q7: Top 10 crime types by number of crimes (bar chart, sorted highest to lowest)
    with col_q7:
        q7_data = active_df['Primary Type'].value_counts().head(10).reset_index()
        q7_data.columns = ['Primary Type', 'Count']
        q7_data = q7_data.sort_values('Count', ascending=True)

        fig_q7 = px.bar(
            q7_data,
            y='Primary Type',
            x='Count',
            text='Count',
            orientation='h',
            title="Q7. Top 10 Crime Types by Total Incidents",
            labels={'Primary Type': 'Crime Type', 'Count': 'Number of Crimes'},
            color_discrete_sequence=['#2563eb']
        )
        fig_q7.update_traces(texttemplate='%{text:,.0f}', textposition='outside')
        fig_q7.update_layout(height=400, margin=dict(l=20, r=20, t=50, b=40))
        st.plotly_chart(fig_q7, use_container_width=True)

    # Q8: Top 5 crime types by number of domestic crimes (bar chart, sorted highest to lowest)
    with col_q8:
        domestic_df = active_df[active_df['Domestic'] == True]
        q8_data = domestic_df['Primary Type'].value_counts().head(5).reset_index()
        q8_data.columns = ['Primary Type', 'Domestic Count']
        q8_data = q8_data.sort_values('Domestic Count', ascending=True)

        fig_q8 = px.bar(
            q8_data,
            y='Primary Type',
            x='Domestic Count',
            text='Domestic Count',
            orientation='h',
            title="Q8. Top 5 Domestic Crime Types",
            labels={'Primary Type': 'Crime Type', 'Domestic Count': 'Domestic Crimes'},
            color_discrete_sequence=['#db2777']
        )
        fig_q8.update_traces(texttemplate='%{text:,.0f}', textposition='outside')
        fig_q8.update_layout(height=400, margin=dict(l=20, r=20, t=50, b=40))
        st.plotly_chart(fig_q8, use_container_width=True)


# ---------------------------------------------------------
# Tab 3: Locations & Matrix Heatmap (Q9 - Q10)
# ---------------------------------------------------------
with tab_location:
    col_q9, col_q10 = st.columns([1, 1])

    # Q9: Top 10 police districts by crime count (bars) and arrest rate % (secondary line)
    with col_q9:
        district_counts = (
            active_df[active_df['District'] != 'Unknown']
            .groupby('District')
            .agg(Crime_Count=('Arrest', 'count'), Arrest_Count=('Arrest', 'sum'))
            .reset_index()
        )
        q9_top10 = district_counts.sort_values('Crime_Count', ascending=False).head(10).copy()
        q9_top10['Arrest_Rate'] = (q9_top10['Arrest_Count'] / q9_top10['Crime_Count']) * 100
        q9_top10['District_Label'] = "Dist " + q9_top10['District'].astype(str)

        # Combo chart using make_subplots
        fig_q9 = make_subplots(specs=[[{"secondary_y": True}]])
        
        # Primary Bar Trace
        fig_q9.add_trace(
            go.Bar(
                x=q9_top10['District_Label'],
                y=q9_top10['Crime_Count'],
                name="Crime Count",
                marker_color='#475569',
                text=q9_top10['Crime_Count'],
                texttemplate='%{text:,.0f}',
                textposition='inside'
            ),
            secondary_y=False
        )

        # Secondary Line Trace
        fig_q9.add_trace(
            go.Scatter(
                x=q9_top10['District_Label'],
                y=q9_top10['Arrest_Rate'],
                name="Arrest Rate %",
                mode='lines+markers+text',
                marker=dict(size=8, color='#dc2626'),
                line=dict(color='#dc2626', width=2.5),
                text=[f"{v:.1f}%" for v in q9_top10['Arrest_Rate']],
                textposition='top center'
            ),
            secondary_y=True
        )

        fig_q9.update_layout(
            title_text="Q9. Top 10 Police Districts: Volume & Arrest Rate %",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            height=420,
            margin=dict(l=20, r=20, t=60, b=40)
        )
        fig_q9.update_yaxes(title_text="Number of Crimes", secondary_y=False)
        fig_q9.update_yaxes(title_text="Arrest Rate (%)", ticksuffix="%", secondary_y=True)
        st.plotly_chart(fig_q9, use_container_width=True)

    # Q10: Heatmap matrix (Day of Week vs Time of Day)
    with col_q10:
        day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        tod_order = ['Night', 'Morning', 'Afternoon', 'Evening']

        matrix_df = (
            active_df.pivot_table(
                index='Day of Week',
                columns='Time of Day',
                values='Date',
                aggfunc='count',
                fill_value=0
            )
            .reindex(index=day_order, columns=tod_order)
        )

        fig_q10 = px.imshow(
            matrix_df,
            labels=dict(x="Time of Day", y="Day of Week", color="Crimes"),
            x=tod_order,
            y=day_order,
            color_continuous_scale="YlOrRd",
            text_auto=True,
            title="Q10. Crime Density Heatmap: Day of Week vs. Time of Day"
        )
        fig_q10.update_layout(height=420, margin=dict(l=20, r=20, t=60, b=40))
        st.plotly_chart(fig_q10, use_container_width=True)
