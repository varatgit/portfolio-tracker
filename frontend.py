# frontend_fin.py

import streamlit as st
import pandas as pd
from datetime import date
from backend import (
    add_asset, add_transaction, get_all_assets, get_all_asset_classes,
    get_asset_by_ticker, get_all_transactions, update_asset_name, delete_asset,
    delete_transaction, get_insights, get_total_portfolio_value
)

st.set_page_config(layout="wide")

st.title("💰 Financial Portfolio Tracker")

# --- Tabs for navigation ---
tab_dashboard, tab_assets, tab_transactions, tab_insights = st.tabs([
    "Dashboard", "Asset Management", "Transactions", "Business Insights"
])

# --- Dashboard Tab ---
with tab_dashboard:
    st.header("Dashboard Summary")
    
    total_value = get_total_portfolio_value()
    col1, col2 = st.columns(2)
    with col1:
        st.metric(label="Total Portfolio Value", value=f"${total_value:,.2f}")
    
    with col2:
        st.write("### Portfolio Breakdown by Asset Class")
        insights = get_insights()
        asset_breakdown = insights.get('assets_by_type', {})
        if asset_breakdown:
            df = pd.DataFrame(asset_breakdown.items(), columns=['Asset Class', 'Number of Holdings'])
            st.bar_chart(df.set_index('Asset Class'))
        else:
            st.info("No assets found. Add some assets to see a breakdown.")

    st.write("---")
    st.subheader("Recent Transactions")
    all_transactions = get_all_transactions()
    if all_transactions:
        df_transactions = pd.DataFrame(
            all_transactions,
            columns=['ID', 'Ticker', 'Date', 'Type', 'Quantity', 'Price', 'Total Cost']
        )
        st.dataframe(df_transactions[['Ticker', 'Date', 'Type', 'Quantity', 'Price', 'Total Cost']], use_container_width=True)
    else:
        st.info("No transactions logged yet.")

# --- Asset Management Tab (CRUD) ---
with tab_assets:
    st.header("Manage Your Assets")
    
    st.subheader("Add a New Asset")
    asset_classes = get_all_asset_classes()
    class_df = pd.DataFrame(asset_classes, columns=['id', 'name'])
    
    with st.form("add_asset_form"):
        ticker = st.text_input("Ticker Symbol (e.g., AAPL)")
        asset_class_name = st.selectbox(
            "Asset Class",
            class_df['name'].tolist()
        )
        asset_class_id = class_df[class_df['name'] == asset_class_name]['id'].iloc[0]
        name = st.text_input("Company/Asset Name")
        
        submitted = st.form_submit_button("Add Asset")
        if submitted and ticker and name:
            if add_asset(ticker.upper(), int(asset_class_id), name):
                st.success(f"Asset '{ticker.upper()}' added successfully!")
            else:
                st.error("Failed to add asset.")

    st.subheader("Current Holdings")
    assets = get_all_assets()
    if assets:
        df_assets = pd.DataFrame(assets, columns=['ID', 'Ticker', 'Name', 'Class'])
        st.dataframe(df_assets[['Ticker', 'Name', 'Class']], use_container_width=True)
        
        st.write("---")
        st.subheader("Update or Delete an Asset")
        update_delete_col1, update_delete_col2 = st.columns(2)
        
        with update_delete_col1:
            asset_to_update = st.selectbox("Select Asset to Update", df_assets['Ticker'].tolist())
            new_name = st.text_input(f"New Name for {asset_to_update}")
            if st.button("Update Name"):
                asset_id = df_assets[df_assets['Ticker'] == asset_to_update]['ID'].iloc[0]
                if update_asset_name(asset_id, new_name):
                    st.success(f"Name for {asset_to_update} updated.")
                else:
                    st.error("Failed to update name.")

        with update_delete_col2:
            asset_to_delete = st.selectbox("Select Asset to Delete", df_assets['Ticker'].tolist())
            if st.button("Delete Asset", key="delete_asset_button"):
                asset_id = df_assets[df_assets['Ticker'] == asset_to_delete]['ID'].iloc[0]
                if delete_asset(asset_id):
                    st.success(f"Asset {asset_to_delete} and all its transactions deleted.")
                else:
                    st.error("Failed to delete asset.")
    else:
        st.info("No assets found. Add an asset to get started.")

# --- Transactions Tab (CRUD) ---
with tab_transactions:
    st.header("Log Transactions")
    
    st.subheader("Add a New Transaction")
    assets_for_tx = get_all_assets()
    if not assets_for_tx:
        st.warning("Please add an asset first in the 'Asset Management' tab to log a transaction.")
    else:
        tx_tickers = [row[1] for row in assets_for_tx]
        with st.form("add_transaction_form"):
            selected_ticker = st.selectbox("Select Asset", tx_tickers)
            asset_id = next((item[0] for item in assets_for_tx if item[1] == selected_ticker), None)
            
            tx_type = st.selectbox("Transaction Type", ['BUY', 'SELL', 'DIVIDEND'])
            tx_date = st.date_input("Transaction Date", date.today())
            quantity = st.number_input("Quantity", min_value=0.01, format="%.2f")
            price = st.number_input("Price per Share", min_value=0.01, format="%.2f")
            
            submitted_tx = st.form_submit_button("Add Transaction")
            if submitted_tx:
                if add_transaction(asset_id, tx_date, tx_type, quantity, price):
                    st.success("Transaction added successfully!")
                else:
                    st.error("Failed to add transaction.")

    st.write("---")
    st.subheader("Transaction History")
    all_transactions = get_all_transactions()
    if all_transactions:
        df_transactions = pd.DataFrame(
            all_transactions,
            columns=['ID', 'Ticker', 'Date', 'Type', 'Quantity', 'Price', 'Total Cost']
        )
        st.dataframe(df_transactions[['Ticker', 'Date', 'Type', 'Quantity', 'Price', 'Total Cost']], use_container_width=True)
        
        st.write("---")
        st.subheader("Delete a Transaction")
        transaction_to_delete_id = st.selectbox(
            "Select Transaction to Delete",
            df_transactions['ID'].tolist(),
            format_func=lambda x: f"ID: {x} | Ticker: {df_transactions[df_transactions['ID'] == x]['Ticker'].iloc[0]} | Type: {df_transactions[df_transactions['ID'] == x]['Type'].iloc[0]}"
        )
        if st.button("Delete Selected Transaction"):
            if delete_transaction(transaction_to_delete_id):
                st.success("Transaction deleted.")
            else:
                st.error("Failed to delete transaction.")
    else:
        st.info("No transactions logged yet.")

# --- Business Insights Tab ---
with tab_insights:
    st.header("Portfolio Business Insights")
    st.markdown("Here you can find key metrics and insights about your portfolio.")
    
    insights = get_insights()

    if insights:
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            st.metric("Total Investment (Buy)", f"${insights.get('total_investment', 0):,.2f}")

        with col2:
            st.metric("Avg. Cost per Share", f"${insights.get('avg_cost_per_share', 0):,.2f}")
            
        with col3:
            st.metric("Highest Transaction", f"${insights.get('max_transaction_value', 0):,.2f}")

        with col4:
            st.metric("Lowest Transaction", f"${insights.get('min_transaction_value', 0):,.2f}")
            
        with col5:
            st.metric("Number of Assets", f"{len(get_all_assets())}")

        st.write("---")
        st.subheader("Asset Breakdown")
        
        asset_breakdown = insights.get('assets_by_type', {})
        if asset_breakdown:
            df_breakdown = pd.DataFrame(asset_breakdown.items(), columns=['Asset Class', 'Count'])
            st.write("### Total Count of Assets by Class")
            st.bar_chart(df_breakdown.set_index('Asset Class'))
            st.write("This chart shows the distribution of your assets across different classes.")
        else:
            st.info("No assets to display insights for.")
    else:
        st.warning("No data available to generate insights.")