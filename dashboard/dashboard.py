"""Initial dashboard page"""
import streamlit as st


st.markdown("""
    <style>

        [data-testid="stSidebar"] {
            background-color: #d9b731ff;
        }

        [data-testid="stSidebar"] * {
            color: #171f2bff !important;
            font-weight: 600;
            letter-spacing: 0.5px;
            text-transform: uppercase; /* <<< this makes all text capitalised */
        }

        [data-testid="stSidebar"] h1, 
        [data-testid="stSidebar"] h2, 
        [data-testid="stSidebar"] h3 {
            color: black !important;
        }
    </style>
""", unsafe_allow_html=True)


pg = st.navigation([st.Page("power_generation.py"),
                   st.Page("carbon_insights.py"), st.Page("energy_prices.py"), st.Page("power_outages.py"), st.Page("sign_up.py")])
pg.run()
