"""Initial dashboard page"""
import streamlit as st
import base64
from pathlib import Path
import mimetypes


# Sidebar styling
st.markdown("""
    <style>
        /* Sidebar background + text */
        [data-testid="stSidebar"] {
            background-color: #fec70f;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
        }

        [data-testid="stSidebar"] * {
            color: #171f2bff !important;
            font-weight: 600;
            letter-spacing: 0.5px;
            text-transform: uppercase;
        }

        [data-testid="stSidebar"] h1, 
        [data-testid="stSidebar"] h2, 
        [data-testid="stSidebar"] h3 {
            color: black !important;
        }

        /* Logo container locked to bottom */
        .sidebar-logo {
            position: absolute;
            bottom: -450px;
            left: 0;
            width: 100%;
            text-align: center;
        }

        /* Logo styling */
        .sidebar-logo img {
            width: 100%;          
            max-width: 500px;     
            aspect-ratio: 1 / 1;  
            border-radius: 12px;  
            object-fit: contain;
            opacity: 1;
            transition: transform 0.2s ease-in-out;
        }

        .sidebar-logo img:hover {
            transform: scale(1.05);
        }
    </style>
""", unsafe_allow_html=True)


# Logo loader
def get_base64_image(image_path: str) -> str:
    """Convert image to base64 string for embedding."""
    image_path = Path(image_path)
    if not image_path.exists():
        st.warning(f"Logo not found at: {image_path.resolve()}")
        return ""
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode()


logo_path = Path("image.png")
logo_base64 = get_base64_image(logo_path)
mime_type = mimetypes.guess_type(logo_path)[0] or "image/png"

# Embed the logo in the sidebar
with st.sidebar:
    st.markdown(
        f"""
        <div class="sidebar-logo">
            <img src="data:{mime_type};base64,{logo_base64}" alt="Logo">
        </div>
        """,
        unsafe_allow_html=True
    )


# Navigation pages
pg = st.navigation([
    st.Page("power_generation.py"),
    st.Page("carbon_insights.py"),
    st.Page("energy_prices.py"),
    st.Page("power_outages.py"),
    st.Page("sign_up.py")
])

pg.run()
