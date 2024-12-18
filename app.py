import streamlit as st
import sqlite3
import base64

# Set the page configuration
st.set_page_config(page_title="Air Quality Index", layout="wide")

@st.cache_data
def get_img_as_base64(file): 
    with open(file, "rb") as f: 
        data = f.read() 
        return base64.b64encode(data).decode()

img = get_img_as_base64("sm.jpg")

page_bg_img = f"""
<style>
[data-testid="stAppViewContainer"] {{
    background-image: url("data:image/png;base64,{img}");
    background-size: cover;
}}

[data-testid="stHeader"]{{
background: rgba(0,0,0,0)    
}}

[data-testid="stToolbar"]{{
right:2rem;    
}}
</style>
"""

st.markdown(page_bg_img, unsafe_allow_html=True)

if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False
    st.session_state["username"] = None
if "show_login" not in st.session_state:
    st.session_state["show_login"] = True

# Initialize database
def init_db():
    """Create users table if it doesn't exist."""
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    c.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            password TEXT NOT NULL
        )
        """
    )
    conn.commit()
    conn.close()

def add_user(username, password):
    """Add a new user to the database."""
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    try:
        c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False  # Username already exists
    finally:
        conn.close()

def authenticate_user(username, password):
    """Check if the username and password are valid."""
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
    user = c.fetchone()
    conn.close()
    return user

def show_sign_up_page():
    st.markdown(
        """
        <h1 style="text-align: center; color: #34D9CE;">
            🌐 Sign Up for an Account
        </h1>
        """,
        unsafe_allow_html=True,
    )


    if not st.session_state["authenticated"]:
        col1, col2, col3 = st.columns([1, 2, 1])  
        with col2:
            username = st.text_input("Enter Username:")
            password = st.text_input("Enter Password:", type="password")
            confirm_password = st.text_input("Confirm Password:", type="password")

            if st.button("Sign Up"):
                if not username or not password:
                    st.warning("Please fill out all fields.")
                elif password != confirm_password:
                    st.error("Passwords do not match!")
                elif add_user(username, password):
                    st.success("Account created successfully! Please log in.")
                    st.session_state["show_login"] = True
                else:
                    st.error("Username already exists! Please choose a different one.")

            if st.button("Back to Login"):
                st.session_state["show_login"] = True
                st.rerun()

def show_login_page():
    """Display the login page."""
    st.markdown(
        """
        <h1 style="text-align: center; color: #34D9CE;">
             Login to access AQI Dashboard
        </h1>
        """,
        unsafe_allow_html=True,
    )

   
    col1, col2, col3 = st.columns([1, 2, 1])  
    with col2:
        username = st.text_input("Username:")
        password = st.text_input("Password:", type="password")

        
        button_col1, button_col2,button_col3 = st.columns([1, 1.5,1])
        with button_col2:
            if st.button("Login", use_container_width=True):
                if authenticate_user(username, password):
                    st.session_state["authenticated"] = True
                    st.session_state["username"] = username
                    st.rerun()
                else:
                    st.error("Invalid username or password!")
        
            if st.button("Sign Up", use_container_width=True):
                st.session_state["show_login"] = False
                st.rerun()

def show_dashboard():
    """Display the dashboard page."""
    st.markdown(
        f"""
        <h1 style="text-align: center; color: #34D9CE;">
            WELCOME TO 📊 AIR QUALITY INSIGHTS DASHBOARD
        </h1>
        """,
        unsafe_allow_html=True,
    )

    # Power BI Dashboard URL
    power_bi_url = "https://app.powerbi.com/view?r=eyJrIjoiMzg4OTViZmUtZTg3MS00MzMxLTlkYTItMGY1NGVmN2MxZWRmIiwidCI6ImY4ZmM1YmRlLWEzYzMtNDExMy04NDYzLWVhY2JmZmIxZjA4OCJ9"

    # Embed Power BI dashboard using an iframe
    st.markdown(
        f"""
        <div style="
            border: 3px solid #34D9CE; 
            border-radius: 8px; 
            padding: 10px; 
            background-color: black; 
            box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.1); 
            margin-bottom: 20px;">
            <iframe 
                src="{power_bi_url}" 
                width="100%" 
                height="800" 
                frameborder="0" 
                allowfullscreen="true">
            </iframe>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Logout button
    if st.sidebar.button("Logout"):
        st.session_state.clear()  # Reset session state
        st.rerun()

# Initialize database
init_db()

# Show the appropriate page based on authentication and navigation
if st.session_state["authenticated"]:
    show_dashboard()
elif st.session_state["show_login"]:
    show_login_page()
else:
    show_sign_up_page()