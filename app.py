import streamlit as st
import pandas as pd
from datetime import date, datetime
from dateutil.relativedelta import relativedelta
import calendar
import plotly.graph_objects as go
import plotly.express as px
import textwrap

# Initialize session state
if "page" not in st.session_state:
    st.session_state.page = "Assumptions"

if "form_data" not in st.session_state:
    st.session_state.form_data = {}

if "calculate" not in st.session_state:
    st.session_state.calculate = False

st.title("📊 SaaS Financial Model")

with st.form("single_page_form", clear_on_submit=False):
    # Core Parameters - Column 1
    st.subheader("Core Parameters")
    col1, col2 = st.columns(2)
    
    with col1:
        # Year selection only
        current_year = date.today().year
        years = list(range(current_year, current_year + 6))  # Next 5 years
        selected_year = st.selectbox("Launch Year", years, index=1)  # Default to next year
        
        # Create and store the date object (always January 1st of selected year)
        kick_off_date = date(int(selected_year), 1, 1)  # Fixed to January (month=1)
        
        # Store in session state
        st.session_state.form_data['kick_off_date'] = kick_off_date

        st.session_state.form_data['subscription_price'] = st.number_input("Subscription Price ($)",min_value=0.0,value=25.5,step=0.5, format="%.2f")
        st.session_state.form_data['free_trial_days'] = st.number_input("Free Trial (Days)", min_value=0, max_value=28,value=7,step=1)

    
    with col2:
        
        st.session_state.form_data['trial_to_paid'] = st.number_input("Trial To Paid Rate %", min_value=0, max_value=100,value=25,step=5) / 100
        st.session_state.form_data['churn_rate'] = st.number_input("Monthly Churn %", min_value=0, max_value=100,value=25,step=5) / 100
    
    # Traffic Inputs
    st.subheader("Traffic Parameters")
    traffic_col1, traffic_col2, traffic_col3 = st.columns(3)
    
    with traffic_col1:
        st.session_state.form_data['sem_traffic_m1'] = st.number_input(
            "SEM Traffic - First Month", min_value=0, 
            value=100000, step=1000, format="%d")
    with traffic_col2:
        st.session_state.form_data['seo_traffic_m1'] = st.number_input(
            "SEO Traffic - First Month", min_value=0, 
            value=100000, step=1000, format="%d")
    
    # Growth Rates Section
    st.subheader("Traffic Monthly Growth Rates by Year")
    
    # SEM Growth Rates
    st.markdown("**SEM Web/App Traffic Monthly Growth by Year**")
    _cols = st.columns(5)
    with _cols[0]:
        st.session_state.form_data['sem_traffic_gr_y1'] = st.number_input("Year 1 (%)", 0.0, 100.0, 2.0, 0.5, key="_y1") / 100
    with _cols[1]:
        st.session_state.form_data['sem_traffic_gr_y2'] = st.number_input("Year 2 (%)", 0.0, 100.0, 2.0, 0.5, key="_y2") / 100
    with _cols[2]:
        st.session_state.form_data['sem_traffic_gr_y3'] = st.number_input("Year 3 (%)", 0.0, 100.0, 2.0, 0.5, key="sem_y3") / 100
    with _cols[3]:
        st.session_state.form_data['sem_traffic_gr_y4'] = st.number_input("Year 4 (%)", 0.0, 100.0, 2.0, 0.5, key="sem_y4") / 100
    with _cols[4]:
        st.session_state.form_data['sem_traffic_gr_y5'] = st.number_input("Year 5 (%)", 0.0, 100.0, 2.0, 0.5, key="sem_y5") / 100
    
    # SEO Growth Rates
    st.markdown("**SEO - Web/App Traffic Monthly Growth by Year**")
    seo_cols = st.columns(5)
    with seo_cols[0]:
        st.session_state.form_data['seo_traffic_gr_y1'] = st.number_input("Year 1 (%)", 0.0, 100.0, 2.0, 0.5, key="seo_y1") / 100
    with seo_cols[1]:
        st.session_state.form_data['seo_traffic_gr_y2'] = st.number_input("Year 2 (%)", 0.0, 100.0, 2.0, 0.5, key="seo_y2") / 100
    with seo_cols[2]:
        st.session_state.form_data['seo_traffic_gr_y3'] = st.number_input("Year 3 (%)", 0.0, 100.0, 2.0, 0.5, key="seo_y3") / 100
    with seo_cols[3]:
        st.session_state.form_data['seo_traffic_gr_y4'] = st.number_input("Year 4 (%)", 0.0, 100.0, 2.0, 0.5, key="seo_y4") / 100
    with seo_cols[4]:
        st.session_state.form_data['seo_traffic_gr_y5'] = st.number_input("Year 5 (%)", 0.0, 100.0, 2.0, 0.5, key="seo_y5") / 100
    
    # Conversion Rates Section
    st.subheader("Conversion Rate Assumptions")
    
    # SEM Conversion Rates
    st.markdown("**SEM Conversion Rates**")
    sem_cr_cols = st.columns(5)
    with sem_cr_cols[0]:
        st.session_state.form_data['sem_cr_y1'] = st.number_input("Year 1", 0.0, 100.0, 4.0, 0.5, key="sem_cr_y1") / 100
    with sem_cr_cols[1]:
        st.session_state.form_data['sem_cr_y2'] = st.number_input("Year 2", 0.0, 100.0, 4.5, 0.5, key="sem_cr_y2") / 100
    with sem_cr_cols[2]:
        st.session_state.form_data['sem_cr_y3'] = st.number_input("Year 3", 0.0, 100.0, 5.0, 0.5, key="sem_cr_y3") / 100
    with sem_cr_cols[3]:
        st.session_state.form_data['sem_cr_y4'] = st.number_input("Year 4", 0.0, 100.0, 5.5, 0.5, key="sem_cr_y4") / 100
    with sem_cr_cols[4]:
        st.session_state.form_data['sem_cr_y5'] = st.number_input("Year 5", 0.0, 100.0, 6.0, 0.5, key="sem_cr_y5") / 100
    
    # SEO Conversion Rates
    st.markdown("**SEO Conversion Rates**")
    seo_cr_cols = st.columns(5)
    with seo_cr_cols[0]:
        st.session_state.form_data['seo_cr_y1'] = st.number_input("Year 1", 0.0, 100.0, 4.0, 0.5, key="seo_cr_y1") / 100
    with seo_cr_cols[1]:
        st.session_state.form_data['seo_cr_y2'] = st.number_input("Year 2", 0.0, 100.0, 4.5, 0.5, key="seo_cr_y2") / 100
    with seo_cr_cols[2]:
        st.session_state.form_data['seo_cr_y3'] = st.number_input("Year 3", 0.0, 100.0, 5.0, 0.5, key="seo_cr_y3") / 100
    with seo_cr_cols[3]:
        st.session_state.form_data['seo_cr_y4'] = st.number_input("Year 4", 0.0, 100.0, 5.5, 0.5, key="seo_cr_y4") / 100
    with seo_cr_cols[4]:
        st.session_state.form_data['seo_cr_y5'] = st.number_input("Year 5", 0.0, 100.0, 6.0, 0.5, key="seo_cr_y5") / 100

    # Affiliate Marketing Section
    st.subheader("Affiliate Marketing Parameters")

    # First Month Subscriptions
    st.session_state.form_data['subs_affiliate_marketing_m1'] = st.number_input(
        "Affiliate Marketing Subscriptions - First Month",  
        min_value=0, value=1000, step=1000, format="%d")

    # Affiliate Growth Rates
    st.markdown("**Affiliate Subscriptions Growth**")
    aff_cols = st.columns(5)
    with aff_cols[0]:
        st.session_state.form_data['affiliate_subs_gr_y1'] = st.number_input("Year 1", 0.0, 100.0, 2.0, 0.5, key="aff_y1") / 100
    with aff_cols[1]:
        st.session_state.form_data['affiliate_subs_gr_y2'] = st.number_input("Year 2", 0.0, 100.0, 2.0, 0.5, key="aff_y2") / 100
    with aff_cols[2]:
        st.session_state.form_data['affiliate_subs_gr_y3'] = st.number_input("Year 3", 0.0, 100.0, 2.0, 0.5, key="aff_y3") / 100
    with aff_cols[3]:
        st.session_state.form_data['affiliate_subs_gr_y4'] = st.number_input("Year 4", 0.0, 100.0, 2.0, 0.5, key="aff_y4") / 100
    with aff_cols[4]:
        st.session_state.form_data['affiliate_subs_gr_y5'] = st.number_input("Year 5", 0.0, 100.0, 2.0, 0.5, key="aff_y5") / 100

    # Cost Assumptions Section
    st.subheader("Cost Assumptions")
    cost_col1, cost_col2 = st.columns(2)
    
    with cost_col1:
        st.session_state.form_data['sem_cpa'] = st.number_input("SEM CPA ($)", min_value=0.0, value=20.0, step=0.5, format="%.2f")
        st.session_state.form_data['affiliate_cpa'] = st.number_input("Affiliate Marketing Pay-per-Subscription ($)", min_value=0.0, value=11.0, step=0.5, format="%.2f")
        st.session_state.form_data['ccp_rate'] = st.number_input("Credit Card Processing Cost (%)", min_value=0.0, value=10.0, step=0.5, format="%.2f") / 100
        st.session_state.form_data['refund_rate'] = st.number_input("Refund Rate (%)", min_value=0.0, value=5.0, step=0.5, format="%.2f") / 100
        
    with cost_col2:
        st.session_state.form_data['chb_rate'] = st.number_input("Chargeback Rate (%)", min_value=0.0, value=0.5, step=0.5, format="%.2f") / 100
        st.session_state.form_data['monthly_web_hosting_cost'] = st.number_input("Monthly Web Hosting Cost ($)", min_value=0, value=300, step=50)
        st.session_state.form_data['monthly_techsoft_cost'] = st.number_input("Monthly Technology & Software Cost ($)", min_value=0, value=300, step=50)
        st.session_state.form_data['monthly_labor_cost'] = st.number_input("Monthly Labor Cost ($)", min_value=0, value=10000, step=1000)
    
    # Calculate button
    if st.form_submit_button("Calculate Projections"):
        st.session_state.calculate = True
        st.rerun()

# Calculations and Results
if st.session_state.calculate:
    # Extract all variables from session state
    form_data = st.session_state.form_data
    kick_off_date = form_data['kick_off_date']
    subscription_price = form_data['subscription_price']
    free_trial_days = form_data['free_trial_days']
    trial_to_paid = form_data['trial_to_paid']
    churn_rate = form_data['churn_rate']
    sem_traffic_m1 = form_data['sem_traffic_m1']
    seo_traffic_m1 = form_data['seo_traffic_m1']
    subs_affiliate_marketing_m1 = form_data['subs_affiliate_marketing_m1']
    sem_traffic_gr_y1 = form_data['sem_traffic_gr_y1']
    sem_traffic_gr_y2 = form_data['sem_traffic_gr_y2']
    sem_traffic_gr_y3 = form_data['sem_traffic_gr_y3']
    sem_traffic_gr_y4 = form_data['sem_traffic_gr_y4']
    sem_traffic_gr_y5 = form_data['sem_traffic_gr_y5']
    seo_traffic_gr_y1 = form_data['seo_traffic_gr_y1']
    seo_traffic_gr_y2 = form_data['seo_traffic_gr_y2']
    seo_traffic_gr_y3 = form_data['seo_traffic_gr_y3']
    seo_traffic_gr_y4 = form_data['seo_traffic_gr_y4']
    seo_traffic_gr_y5 = form_data['seo_traffic_gr_y5']
    affiliate_subs_gr_y1 = form_data['affiliate_subs_gr_y1']
    affiliate_subs_gr_y2 = form_data['affiliate_subs_gr_y2']
    affiliate_subs_gr_y3 = form_data['affiliate_subs_gr_y3']
    affiliate_subs_gr_y4 = form_data['affiliate_subs_gr_y4']
    affiliate_subs_gr_y5 = form_data['affiliate_subs_gr_y5']
    sem_cr_y1 = form_data['sem_cr_y1']
    sem_cr_y2 = form_data['sem_cr_y2']
    sem_cr_y3 = form_data['sem_cr_y3']
    sem_cr_y4 = form_data['sem_cr_y4']
    sem_cr_y5 = form_data['sem_cr_y5']
    seo_cr_y1 = form_data['seo_cr_y1']
    seo_cr_y2 = form_data['seo_cr_y2']
    seo_cr_y3 = form_data['seo_cr_y3']
    seo_cr_y4 = form_data['seo_cr_y4']
    seo_cr_y5 = form_data['seo_cr_y5']
    sem_cpa = form_data['sem_cpa']
    affiliate_cpa = form_data['affiliate_cpa']
    ccp_rate = form_data['ccp_rate']
    refund_rate = form_data['refund_rate']
    chb_rate = form_data['chb_rate']
    monthly_web_hosting_cost = form_data['monthly_web_hosting_cost']
    monthly_techsoft_cost = form_data['monthly_techsoft_cost']
    monthly_labor_cost = form_data['monthly_labor_cost']
    renewal_rate = 1 - churn_rate
    LTV = (subscription_price * trial_to_paid) / (1 - renewal_rate)
    sem_roi=LTV-sem_cpa
    sem_roi_percent=sem_roi/sem_cpa
    affiliate_marketing_roi=LTV-affiliate_cpa
    affiliate_marketing_roi_percent=affiliate_marketing_roi/affiliate_cpa
    

    # First, let's create a function to determine the growth rate based on the month index
    def get_sem_growth_rate(month_idx):
        if month_idx <= 12:  # Year 1
            return 1 + sem_traffic_gr_y1
        elif month_idx <= 24:  # Year 2
            return 1 + sem_traffic_gr_y2
        elif month_idx <= 36:  # Year 3
            return 1 + sem_traffic_gr_y3
        elif month_idx <= 48:  # Year 4
            return 1 + sem_traffic_gr_y4
        else:  # Year 5
            return 1 + sem_traffic_gr_y5

    def get_sem_cr(month_idx):
        if month_idx <= 12:    # Year 1
            return sem_cr_y1
        elif month_idx <= 24:  # Year 2
            return sem_cr_y2
        elif month_idx <= 36:  # Year 3
            return sem_cr_y3
        elif month_idx <= 48:  # Year 4
            return sem_cr_y4
        else:                  # Year 5
            return sem_cr_y5  

    def get_seo_growth_rate(month_idx):
        if month_idx <= 12:  # Year 1
            return 1 + seo_traffic_gr_y1
        elif month_idx <= 24:  # Year 2
            return 1 + seo_traffic_gr_y2
        elif month_idx <= 36:  # Year 3
            return 1 + seo_traffic_gr_y3
        elif month_idx <= 48:  # Year 4
            return 1 + seo_traffic_gr_y4
        else:  # Year 5
            return 1 + seo_traffic_gr_y5

    def get_seo_cr(month_idx):
        if month_idx <= 12:    # Year 1
            return seo_cr_y1
        elif month_idx <= 24:  # Year 2
            return seo_cr_y2
        elif month_idx <= 36:  # Year 3
            return seo_cr_y3
        elif month_idx <= 48:  # Year 4
            return seo_cr_y4
        else:                  # Year 5
            return seo_cr_y5      
        
    def get_afmar_growth_rate(month_idx):
        if month_idx <= 12:  # Year 1
            return 1 + affiliate_subs_gr_y1
        elif month_idx <= 24:  # Year 2
            return 1 + affiliate_subs_gr_y2
        elif month_idx <= 36:  # Year 3
            return 1 + affiliate_subs_gr_y3
        elif month_idx <= 48:  # Year 4
            return 1 + affiliate_subs_gr_y4
        else:  # Year 5
            return 1 + affiliate_subs_gr_y5

    # Recurring revenue and financials dataframe
    months = [kick_off_date + relativedelta(months=i) for i in range(60)]
    # Create DataFrame
    df = pd.DataFrame({
        "Month": [kick_off_date + relativedelta(months=i) for i in range(60)],
        "Year": [month.year for month in months],  # Extract year from each date
        "Days Count": [calendar.monthrange(month.year, month.month)[1] for month in months],
    })
    df["Cross-Over Month Trial-To-Paid"] = free_trial_days / df["Days Count"]
    df["Trial-To-Paid Within Month"] = 1 - df["Cross-Over Month Trial-To-Paid"]
    
    df["SEM - Paid Traffic"] = 0.0
    df.at[0, "SEM - Paid Traffic"] = sem_traffic_m1  # Set first month value

    # Calculate subsequent months
    for i in range(1, 60):
        sem_growth_rate = get_sem_growth_rate(i)
        df.at[i, "SEM - Paid Traffic"] = df.at[i-1, "SEM - Paid Traffic"] * sem_growth_rate

    df["SEO - Organic Traffic"] = 0.0
    df.at[0, "SEO - Organic Traffic"] = seo_traffic_m1  # Set first month value

    # Calculate subsequent months
    for i in range(1, 60):
        seo_growth_rate = get_seo_growth_rate(i)
        df.at[i, "SEO - Organic Traffic"] = df.at[i-1, "SEO - Organic Traffic"] * seo_growth_rate

    df["Affiliate Marketing Subscriptions"] = 0.0
    df.at[0, "Affiliate Marketing Subscriptions"] = subs_affiliate_marketing_m1  # Set first month value (10,000)

    # Calculate subsequent months (with correct variable name)
    for i in range(1, 60):
        afmar_growth_rate = get_afmar_growth_rate(i)
        df.at[i, "Affiliate Marketing Subscriptions"] = df.at[i-1, "Affiliate Marketing Subscriptions"] * afmar_growth_rate
        
    df["SEM Subscriptions"] = df["SEM - Paid Traffic"] * df.index.map(get_sem_cr)
    df["SEO Subscriptions"] = df["SEO - Organic Traffic"] * df.index.map(get_seo_cr)
    df["Total Monthly Subscriptions"] = df["SEM Subscriptions"] + df["SEO Subscriptions"] + df["Affiliate Marketing Subscriptions"]

    # Initialize the new column
    df["Trial To Paid Transactions Count"] = 0.0

    # First row calculation
    df.at[0, "Trial To Paid Transactions Count"] = (
        df.at[0, "Total Monthly Subscriptions"] * 
        df.at[0, "Trial-To-Paid Within Month"] * 
        trial_to_paid
    )

    # Subsequent rows calculation
    for i in range(1, len(df)):
        df.at[i, "Trial To Paid Transactions Count"] = (
            (df.at[i, "Total Monthly Subscriptions"] * df.at[i, "Trial-To-Paid Within Month"] * trial_to_paid) +
            (df.at[i-1, "Total Monthly Subscriptions"] * df.at[i-1, "Cross-Over Month Trial-To-Paid"] * trial_to_paid)
        )

    df["Monthly Renewal Transactions Count"] = 0.0
    for i in range(1, len(df)):
        prev_ttp = df.loc[i - 1, "Trial To Paid Transactions Count"]
        renewal_prev = df.loc[i - 1, "Monthly Renewal Transactions Count"]
        df.loc[i, "Monthly Renewal Transactions Count"] = (prev_ttp + renewal_prev) * (1 - churn_rate)  

    df['New Monthly Recurring Revenue MRR'] = df["Trial To Paid Transactions Count"] * subscription_price
    df['Renewal Recurring Revenue MRR'] = df["Monthly Renewal Transactions Count"] * subscription_price
    df['Total Monthly Recurring Revenue MRR'] = df['Renewal Recurring Revenue MRR'] + df['New Monthly Recurring Revenue MRR']
    df['Chargebacks'] = df['Total Monthly Recurring Revenue MRR'] * chb_rate
    df['Refunds'] = df['Total Monthly Recurring Revenue MRR'] * refund_rate
    df['Income'] = df['Total Monthly Recurring Revenue MRR'] - df['Refunds'] - df['Chargebacks']
    df['Credit Card Processing'] = df['Total Monthly Recurring Revenue MRR'] * ccp_rate
    df['Web Hosting'] = monthly_web_hosting_cost
    df['Cost of Goods/Services Sold'] = df['Credit Card Processing'] + df['Web Hosting']
    df['Gross Income'] = df['Income'] - df['Cost of Goods/Services Sold']
    df['Labor Cost'] = monthly_labor_cost
    df['SEM Marketing'] = df["SEM Subscriptions"] * sem_cpa
    df['Affiliate Marketing'] = df["Affiliate Marketing Subscriptions"] * affiliate_cpa
    df['Internet Marketing Cost'] = df['Affiliate Marketing'] + df['SEM Marketing']
    df['Technology & Software'] = monthly_techsoft_cost
    df['Earnings Before Taxes'] = df['Gross Income'] - df['Labor Cost'] - df['Internet Marketing Cost'] - df['Technology & Software']
    df['Cash Flow Accumulation'] = df['Earnings Before Taxes']  # Initialize with first month's value

    for i in range(1, len(df)):
        prev_cf = df.loc[i - 1, 'Cash Flow Accumulation']
        current_earnings = df.loc[i, 'Earnings Before Taxes']
        df.loc[i, 'Cash Flow Accumulation'] = prev_cf + current_earnings

    df["Internet Marketing CAC Weighted average"] = ((df["SEM Subscriptions"] * sem_cpa) + (df["Affiliate Marketing Subscriptions"] * affiliate_cpa)) / (df["SEM Subscriptions"] + df["Affiliate Marketing Subscriptions"])

    # dataframe for cac payback period
    first_value = subscription_price * trial_to_paid
    ltv_threshold = LTV * 0.999  # 99% of LTV

    # Initialize list with the first period value
    period_values = [first_value]

    # Generate values until the cumulative sum reaches 99% of LTV
    while sum(period_values) < ltv_threshold:
        next_value = period_values[-1] * renewal_rate
        period_values.append(next_value)

    cumulative_ltv = pd.DataFrame({"Period Value": period_values})
    cumulative_ltv["Accumulated Value"] = cumulative_ltv["Period Value"].cumsum()
    start_month = free_trial_days / 30
    months = [start_month + i for i in range(len(cumulative_ltv))]
    cumulative_ltv["Months"] = months
    
    if LTV < sem_cpa: 
        time_to_recover_sem_cac = "No Pay Back" 
    else: 
        match_row = cumulative_ltv[cumulative_ltv["Accumulated Value"] >= sem_cpa].head(1)
        if not match_row.empty:
            time_to_recover_sem_cac = match_row["Months"].values[0]
        else:
            time_to_recover_sem_cac = "No Pay Back"
        
    if LTV < affiliate_cpa:
        time_to_recover_sem_affiliate_cpa = "No Pay Back"
    else:
        match_row = cumulative_ltv[cumulative_ltv["Accumulated Value"] >= affiliate_cpa].head(1)
        if not match_row.empty:
            time_to_recover_sem_affiliate_cpa = match_row["Months"].values[0]
        else:
            time_to_recover_sem_affiliate_cpa = "No Pay Back"
    
def lookup_payback_period(cac_value):
    if LTV < cac_value:
        return "No Pay Back"
    match_row = cumulative_ltv[cumulative_ltv["Accumulated Value"] >= cac_value].head(1)
    if not match_row.empty:
        return match_row["Months"].values[0]
    else:
        return "No Pay Back"



    df["time_to_recover_Internet_marketing_cac"] = df["Internet Marketing CAC Weighted average"].apply(lookup_payback_period)

    # Financials dataframe consolidation
    df_financials = df[[
        'Month',
        'Year',
        'Total Monthly Recurring Revenue MRR',
        'Chargebacks',
        'Refunds',
        'Income',
        'Credit Card Processing',
        'Web Hosting',
        'Cost of Goods/Services Sold',
        'Gross Income',
        'Labor Cost',
        'SEM Marketing',
        'Affiliate Marketing',
        'Internet Marketing Cost',
        'Technology & Software',
        'Earnings Before Taxes',
        'Cash Flow Accumulation'
    ]].rename(columns={'Total Monthly Recurring Revenue MRR': 'Revenue'})
    df_financials_by_year = df_financials.groupby("Year", as_index=False).sum(numeric_only=True)

    # Show charts
    st.title("📈 Financial Projections Results")
    
    # Financial performance by year chart
    st.subheader("Financial Performance by Year")
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df_financials_by_year["Year"], y=df_financials_by_year["Revenue"],
                             mode='lines+markers', name='Revenue',hovertemplate='$%{y:,.2f}<extra></extra>'))
    fig.add_trace(go.Scatter(x=df_financials_by_year["Year"], y=df_financials_by_year["Income"],
                             mode='lines+markers', name='Income',hovertemplate='$%{y:,.2f}<extra></extra>'))
    fig.add_trace(go.Scatter(x=df_financials_by_year["Year"], y=df_financials_by_year["Gross Income"],
                             mode='lines+markers', name='Gross Income',hovertemplate='$%{y:,.2f}<extra></extra>'))
    fig.add_trace(go.Scatter(x=df_financials_by_year["Year"], y=df_financials_by_year["Earnings Before Taxes"],
                             mode='lines+markers', name='Earnings Before Taxes',hovertemplate='$%{y:,.2f}<extra></extra>'))
    fig.update_layout(
        xaxis_title="Year",
        yaxis_title="Amount ($)",
        plot_bgcolor="white",
        hovermode="x unified",
        legend=dict(title=""),
        yaxis=dict(gridcolor="lightgray")
    )
    st.plotly_chart(fig, use_container_width=True)

    # Cashflow accumulation chart
    st.subheader("Cash Flow Accumulation by Year")
    df_cashflow = df_financials.groupby("Year", as_index=False)["Earnings Before Taxes"].sum()
    df_cashflow["Cash Flow Accumulation"] = df_cashflow["Earnings Before Taxes"].cumsum()
    fig = px.bar(
        df_cashflow,
        x="Year",
        y="Cash Flow Accumulation",
        labels={"Cash Flow Accumulation": "Cash Flow Accumulation ($)"},
        text_auto='.2f',
        color_discrete_sequence=["skyblue"]
    )
    fig.update_traces(
        hovertemplate='$%{y:,.2f}<extra></extra>',
        texttemplate='$%{y:,.2f}',
        textposition='outside'
    )
    fig.update_layout(
        xaxis_title="Year",
        yaxis_title="Cash Flow Accumulation",
        bargap=0.3,
        plot_bgcolor="white",
        yaxis_gridcolor="lightgray"
    )
    st.plotly_chart(fig, use_container_width=True)

    # Revenue split chart
    st.subheader("New vs Renewal MRR")
    df_rev_split = df[[
        'Month',
        'New Monthly Recurring Revenue MRR',
        'Renewal Recurring Revenue MRR' 
    ]]
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df_rev_split["Month"],
        y=df_rev_split["New Monthly Recurring Revenue MRR"],
        mode='lines',
        name='New MRR',
        stackgroup='one',
        hovertemplate='New MRR: $%{y:,.2f}<extra></extra>'
    ))
    fig.add_trace(go.Scatter(
        x=df_rev_split["Month"],
        y=df_rev_split["Renewal Recurring Revenue MRR"],
        mode='lines',
        name='Renewal MRR',
        stackgroup='one',
        hovertemplate='New MRR: $%{y:,.2f}<extra></extra>'
    ))
    fig.update_layout(
        xaxis_title="Month",
        yaxis_title="MRR",
        xaxis=dict(type='category'),
        yaxis=dict(tickformat="$,.2f")
    )
    st.plotly_chart(fig, use_container_width=True)
    
