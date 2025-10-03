"""Initial dashboard page"""
import streamlit as st


pg = st.navigation([st.Page("power_generation.py"),
                   st.Page("carbon_insights.py"), st.Page("energy_prices.py"), st.Page("power_outages_signup.py")])
pg.run()
