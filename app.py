"""
Streamlit Web Interface for Amplify KPI Bot
Provides a GUI for updating KPI calculations and viewing agent data
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta
import logging

from update_kpi_sheets import update_kpi_calculator_for_last_week
from clients import ConnectionChecker
from models import AgentInfoManager
from sheets import GoogleSheetsClient
from utils import get_last_week_dates
import config

# Configure page
st.set_page_config(
    page_title="Amplify KPI Bot",
    page_icon="📊",
    layout="wide"
)

# Initialize session state
if 'last_update_time' not in st.session_state:
    st.session_state.last_update_time = None
if 'connection_status' not in st.session_state:
    st.session_state.connection_status = None

# Sidebar navigation
st.sidebar.title("📊 Amplify KPI Bot")
page = st.sidebar.radio(
    "Navigation",
    ["Home", "Update KPI Calculator", "View Data", "Generate Reports", "Settings"]
)

# Home Page
if page == "Home":
    st.title("Amplify KPI Calculator Bot")
    st.markdown("### Dashboard")
    
    # Check connections
    with st.spinner("Checking connections..."):
        checker = ConnectionChecker()
        connection_results = checker.check_all_connections()
        
        # Update session state
        st.session_state.connection_status = connection_results
    
    # Display connection status
    st.subheader("Connection Status")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if connection_results['tableau']['available']:
            st.success("✅ Tableau")
        else:
            st.error("❌ Tableau")
            st.caption(connection_results['tableau'].get('message', ''))
    
    with col2:
        if connection_results['google_sheets']['available']:
            st.success("✅ Google Sheets")
        else:
            st.error("❌ Google Sheets")
            st.caption(connection_results['google_sheets'].get('message', ''))
    
    with col3:
        if connection_results['salesforce']['available']:
            st.success("✅ Salesforce")
        else:
            st.warning("⚠️ Salesforce")
            st.caption("Using Google Drive CSVs")
    
    with col4:
        # Check Google Drive
        try:
            from clients import GoogleDriveImporter
            importer = GoogleDriveImporter()
            gdrive_status = importer.check_connection()
            if gdrive_status['available']:
                st.success(f"✅ Google Drive")
                st.caption(f"{gdrive_status['files_found']} CSV files")
            else:
                st.warning("⚠️ Google Drive")
        except:
            st.warning("⚠️ Google Drive")
    
    # Last update
    if st.session_state.last_update_time:
        st.info(f"**Last Update:** {st.session_state.last_update_time}")
    else:
        st.info("No updates yet. Click 'Update KPI Calculator' to get started!")
    
    # Quick actions
    st.subheader("Quick Actions")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🔄 Update Now", type="primary", use_container_width=True):
            st.session_state.page = "update"
            st.rerun()
    
    with col2:
        if st.button("📊 View Data", use_container_width=True):
            st.session_state.page = "view"
            st.rerun()

# Update KPI Calculator Page
elif page == "Update KPI Calculator":
    st.title("Update KPI Calculator")
    
    # Date range selector
    week_start, week_end = get_last_week_dates()
    
    col1, col2 = st.columns(2)
    with col1:
        st.info(f"**Default Week:** {week_start.strftime('%m/%d/%Y')} - {week_end.strftime('%m/%d/%Y')}")
    with col2:
        use_custom_week = st.checkbox("Use custom date range")
    
    if use_custom_week:
        col1, col2 = st.columns(2)
        with col1:
            week_start = st.date_input("Start Date", value=week_start)
        with col2:
            week_end = st.date_input("End Date", value=week_end)
        
        week_start = datetime.combine(week_start, datetime.min.time())
        week_end = datetime.combine(week_end, datetime.min.time())
    
    # Update button
    if st.button("🔄 Update KPI Calculator Now", type="primary", use_container_width=True):
        with st.spinner("Updating KPI Calculator..."):
            try:
                results = update_kpi_calculator_for_last_week(
                    update_sheets=True,
                    save_dataframe=True
                )
                
                # Update session state
                st.session_state.last_update_time = datetime.now().strftime("%Y-%m-%d %I:%M %p")
                
                # Display results
                st.success("✅ Update Complete!")
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Agents Updated", results.get('agents_updated', 0))
                with col2:
                    st.metric("Sheets Updated", "✅" if results.get('sheets_updated') else "❌")
                with col3:
                    st.metric("Dataframe Saved", "✅" if results.get('dataframe_saved') else "❌")
                
                # Show data sources
                if results.get('data_sources_used'):
                    st.info(f"**Data Sources:** {', '.join(results['data_sources_used'])}")
                
                # Show file path
                if results.get('dataframe_path'):
                    st.info(f"**Dataframe:** {results['dataframe_path']}")
                
            except Exception as e:
                st.error(f"Error: {str(e)}")
                st.exception(e)

# View Data Page
elif page == "View Data":
    st.title("View Agent Data")
    
    # Agent selector
    st.subheader("Select Agent")
    
    # Load agent list
    try:
        manager = AgentInfoManager()
        agent_list = manager.list_all_agents()
        
        if agent_list:
            agent_name = st.selectbox("Agent", options=agent_list)
            
            if agent_name:
                # Get agent info
                agent_info = manager.get_agent_info(agent_name)
                
                if agent_info:
                    # Display agent info
                    st.subheader(agent_name)
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.info(f"**Team:** {agent_info.get('team_color', 'N/A')}")
                        st.info(f"**FTE Status:** {agent_info.get('emp_fte_status', 'N/A')}")
                    
                    with col2:
                        st.info(f"**Start Date:** {agent_info.get('emp_start_date', 'N/A')}")
                        st.info(f"**ID:** {agent_info.get('_id', 'N/A')}")
                else:
                    st.warning("Agent info not found")
        else:
            st.warning("No agents found. Update KPI Calculator first.")
    except Exception as e:
        st.error(f"Error loading agents: {str(e)}")

# Generate Reports Page
elif page == "Generate Reports":
    st.title("Generate Reports")
    
    st.info("Coming soon! This page will allow you to generate comprehensive reports and export data.")
    
    # Placeholder for future functionality
    st.markdown("""
    **Planned Features:**
    - Generate comprehensive agent dataframes
    - Create team summary reports
    - Export individual agent scorecards
    - Download raw data exports
    """)

# Settings Page
elif page == "Settings":
    st.title("Settings")
    
    # Connection status
    st.subheader("Connection Status")
    if st.button("🔍 Test All Connections"):
        with st.spinner("Testing connections..."):
            checker = ConnectionChecker()
            results = checker.check_all_connections()
            
            for service, status in results.items():
                if status['available']:
                    st.success(f"✅ {service}: {status.get('message', 'Connected')}")
                else:
                    st.error(f"❌ {service}: {status.get('message', 'Not available')}")
    
    # Configuration
    st.subheader("Configuration")
    
    st.markdown(f"""
    - **KPI Calculator Sheet ID:** `{config.GOOGLE_SHEETS_CONFIG['temp_kpi_calculator']['spreadsheet_id']}`
    - **Agent Info Sheet ID:** `{config.GOOGLE_SHEETS_CONFIG['temp_agent_info']['spreadsheet_id']}`
    - **Drive Folder ID:** `{config.GOOGLE_DRIVE_CONFIG['salesforce_csvs_folder_id']}`
    """)
    
    # Logs viewer
    st.subheader("Recent Logs")
    
    try:
        with open('kpi_bot.log', 'r') as f:
            logs = f.readlines()
            # Show last 50 lines
            recent_logs = logs[-50:]
            st.code('\n'.join(recent_logs))
    except FileNotFoundError:
        st.info("No log file found yet.")

# Footer
st.sidebar.markdown("---")
"""Versioning:Major.Minor.Patch"""
st.sidebar.markdown("**Version:** 0.0.1")
st.sidebar.markdown("**Status:** Development")

if __name__ == "__main__":
    # Streamlit app is run with: streamlit run app.py
    pass
